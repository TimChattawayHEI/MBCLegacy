package uk.mbc.legacies;

import java.io.BufferedReader;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * In-app updates (Version 66). Plain Java with no Android classes, so it can be tested off the phone.
 *
 * The APK carries the game in assets/www plus ota.txt, a list of every game file with its SHA-256 (written by the APK
 * build, tools/ota/manifest.py). Each release publishes the same list. When a newer one is out, the files that differ
 * from the APK's own copy are downloaded from raw.githubusercontent.com at that release's exact commit, every one is
 * checked against its hash, and the set is kept in its own folder (b<build>). The page's requests then look in that
 * folder first and fall back to the APK. Nothing changes under a running page: a finished download is only switched in
 * by apply() (a restart) or the next time the app starts.
 *
 * Folder layout under root: active and ready (a build number each), b<build>/ (the changed files, ota.txt and base, the
 * APK build they were made against), stage/ (a download in progress).
 *
 * If the release changed the Android side (its native fingerprint differs from the APK's), files alone can't update
 * it: the state goes to "apk" and the game shows the old download-the-APK card.
 */
public final class Ota {

    /** One parsed ota.txt. */
    public static final class Manifest {
        public int build;
        public String commit = "", nativeFp = "";
        public final Map<String, String> hash = new LinkedHashMap<>();
        public final Map<String, Long> size = new HashMap<>();
        public String text = "";

        public static Manifest parse(String text) throws IOException {
            Manifest m = new Manifest();
            m.text = text;
            boolean head = false;
            for (String line : text.split("\n")) {
                line = line.replace("\r", "");
                if (line.isEmpty()) continue;
                if (line.startsWith("f ")) {
                    String[] p = line.split(" ", 4);
                    if (p.length < 4 || p[1].length() != 64) throw new IOException("bad line");
                    if (!safePath(p[3])) throw new IOException("bad path " + p[3]);
                    m.hash.put(p[3], p[1]);
                    m.size.put(p[3], Long.parseLong(p[2]));
                } else if (line.startsWith("ota ")) head = true;
                else if (line.startsWith("build ")) m.build = Integer.parseInt(line.substring(6).trim());
                else if (line.startsWith("commit ")) m.commit = line.substring(7).trim();
                else if (line.startsWith("native ")) m.nativeFp = line.substring(7).trim();
            }
            if (!head || m.build <= 0 || m.commit.isEmpty() || m.nativeFp.isEmpty()) throw new IOException("not an update list");
            if (!m.commit.matches("[0-9a-f]{7,40}")) throw new IOException("bad commit");
            return m;
        }
    }

    private final File root;
    private final Manifest bundled;
    private final String manifestUrl, rawBase;

    private volatile int active, ready;
    private volatile Manifest activeManifest;
    private volatile File activeDir;

    // what the game reads through otaStatus()
    private volatile String state = "idle", err = "";
    private volatile int latest;
    private volatile long done, total;
    private volatile int files, filesOf;
    private volatile boolean busy;

    /**
     * @param root        the app's own folder for updates (getFilesDir()/ota)
     * @param bundled     the APK's ota.txt, or null (no in-app updates: an APK built before Version 66)
     * @param manifestUrl the latest release's ota.txt
     * @param rawBase     raw file base, the commit and "web/<path>" are added to it
     */
    public Ota(File root, Manifest bundled, String manifestUrl, String rawBase) {
        this.root = root;
        this.bundled = bundled;
        this.manifestUrl = manifestUrl;
        this.rawBase = rawBase.endsWith("/") ? rawBase : rawBase + "/";
        if (bundled == null) state = "off";
    }

    public boolean on() { return bundled != null; }

    /** The game build the page is running: the downloaded one if any, otherwise the APK's. */
    public int build() { return active > 0 ? active : (bundled != null ? bundled.build : 0); }

    // ------------------------------------------------------------------ start-up
    /** Call once as the app starts: switches in a finished download and clears out anything stale. */
    public synchronized void startup() {
        if (bundled == null) return;
        root.mkdirs();
        active = readInt("active");
        ready = readInt("ready");
        if (ready > active && valid(ready)) { active = ready; writeInt("active", active); }
        if (ready != 0) { ready = 0; writeInt("ready", 0); }
        if (active > 0 && !valid(active)) { active = 0; writeInt("active", 0); }
        loadActive();
        // keep only the folder in use
        File[] all = root.listFiles();
        if (all != null) for (File f : all) {
            String n = f.getName();
            if (n.equals("active") || n.equals("ready")) continue;
            if (active > 0 && n.equals("b" + active)) continue;
            delete(f);
        }
    }

    /** A download folder can be used if it's complete and was made against this APK's own files. */
    private boolean valid(int b) {
        if (b <= bundled.build) return false;   // the installed APK is as new or newer
        File d = new File(root, "b" + b);
        if (!new File(d, "ota.txt").isFile()) return false;
        return readText(new File(d, "base")).trim().equals(String.valueOf(bundled.build));
    }

    private void loadActive() {
        activeManifest = null;
        activeDir = null;
        if (active <= 0) return;
        try {
            File d = new File(root, "b" + active);
            activeManifest = Manifest.parse(readText(new File(d, "ota.txt")));
            activeDir = d;
        } catch (IOException e) {
            active = 0;
            writeInt("active", 0);
        }
    }

    // ------------------------------------------------------------------ serving
    /** The downloaded copy of a game file (path relative to the game folder), or null to use the APK's. */
    public File resolve(String rel) {
        File d = activeDir;
        Manifest m = activeManifest;
        if (d == null || m == null || !safePath(rel)) return null;
        if (!m.hash.containsKey(rel)) return null;
        File f = new File(d, rel);
        return f.isFile() ? f : null;
    }

    // ------------------------------------------------------------------ checking and downloading
    /** Look for a newer release on a background thread (does nothing if a look is already running). */
    public void checkAsync() {
        if (bundled == null) return;
        synchronized (this) {
            if (busy) return;
            busy = true;
        }
        Thread t = new Thread(() -> {
            try { check(); } finally { busy = false; }
        }, "mbc-ota");
        t.setDaemon(true);
        t.start();
    }

    /** The look itself; runs on whatever thread calls it. */
    public void check() {
        if (bundled == null) return;
        if (ready > 0 && "ready".equals(state)) return;   // already waiting for a restart
        state = "checking";
        err = "";
        try {
            Manifest m = Manifest.parse(new String(get(manifestUrl, 2_000_000), StandardCharsets.UTF_8));
            latest = m.build;
            if (m.build <= build()) { state = "current"; return; }
            if (!m.nativeFp.equals(bundled.nativeFp)) { state = "apk"; return; }
            if (ready == m.build && valid(m.build)) { state = "ready"; return; }
            stage(m);
            state = "ready";
        } catch (Exception e) {
            err = String.valueOf(e.getMessage());
            state = "error";
        }
    }

    private void stage(Manifest m) throws IOException {
        // the files that differ from the APK's own copy
        List<String> need = new ArrayList<>();
        long bytes = 0;
        for (Map.Entry<String, String> e : m.hash.entrySet()) {
            if (!e.getValue().equals(bundled.hash.get(e.getKey()))) {
                need.add(e.getKey());
                bytes += m.size.get(e.getKey());
            }
        }
        File stage = new File(root, "stage");
        delete(stage);
        if (!stage.mkdirs()) throw new IOException("no space for the update");
        total = bytes; done = 0; files = 0; filesOf = need.size();
        state = "downloading";
        for (String rel : need) {
            String want = m.hash.get(rel);
            File dst = new File(stage, rel);
            File parent = dst.getParentFile();
            if (parent != null) parent.mkdirs();
            File have = localCopy(rel, want);
            if (have != null) copy(have, dst);
            else download(rawUrl(m.commit, rel), dst, want, m.size.get(rel));
            done += m.size.get(rel);
            files++;
        }
        writeText(new File(stage, "ota.txt"), m.text);
        writeText(new File(stage, "base"), String.valueOf(bundled.build));
        File target = new File(root, "b" + m.build);
        if (m.build != active) delete(target);
        if (target.exists() || !stage.renameTo(target)) throw new IOException("could not finish the update");
        // drop an older finished download that never got switched in
        synchronized (this) {
            if (ready > 0 && ready != m.build && ready != active) delete(new File(root, "b" + ready));
            ready = m.build;
            writeInt("ready", ready);
        }
    }

    /** A file we already hold with the right contents (in the folder in use), so it isn't downloaded twice. */
    private File localCopy(String rel, String want) {
        Manifest am = activeManifest;
        File d = activeDir;
        if (am == null || d == null || !want.equals(am.hash.get(rel))) return null;
        File f = new File(d, rel);
        try {
            return f.isFile() && want.equals(sha256(f)) ? f : null;
        } catch (IOException e) {
            return null;
        }
    }

    String rawUrl(String commit, String rel) throws IOException {
        StringBuilder u = new StringBuilder(rawBase).append(commit).append("/web");
        for (String seg : rel.split("/")) u.append('/').append(URLEncoder.encode(seg, "UTF-8").replace("+", "%20"));
        return u.toString();
    }

    private void download(String url, File dst, String want, long size) throws IOException {
        IOException last = null;
        for (int attempt = 0; attempt < 3; attempt++) {
            try {
                HttpURLConnection c = open(url);
                try {
                    if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode() + " for " + dst.getName());
                    MessageDigest md = MessageDigest.getInstance("SHA-256");
                    long n = 0;
                    try (InputStream in = c.getInputStream(); OutputStream out = new FileOutputStream(dst)) {
                        byte[] buf = new byte[32768];
                        int r;
                        while ((r = in.read(buf)) > 0) {
                            out.write(buf, 0, r);
                            md.update(buf, 0, r);
                            n += r;
                            if (n > size) throw new IOException("too big: " + dst.getName());
                        }
                    }
                    if (n != size || !want.equals(hex(md.digest()))) throw new IOException("didn't match: " + dst.getName());
                    return;
                } finally {
                    c.disconnect();
                }
            } catch (IOException e) {
                last = e;
                dst.delete();
            } catch (Exception e) {
                throw new IOException(e.getMessage());
            }
        }
        throw last;
    }

    // ------------------------------------------------------------------ switching in
    /** Switch to the finished download now (the page must be reloaded straight after). */
    public synchronized boolean apply() {
        if (ready <= 0 || !valid(ready)) return false;
        active = ready;
        ready = 0;
        writeInt("active", active);
        writeInt("ready", 0);
        loadActive();
        state = "current";
        return activeDir != null;
    }

    /** For the game: {"state":..., "mine":n, "latest":n, "done":bytes, "total":bytes, "files":k, "of":n, "err":"..."} */
    public String statusJson() {
        return "{\"state\":\"" + state + "\",\"mine\":" + build() + ",\"latest\":" + latest
                + ",\"done\":" + done + ",\"total\":" + total + ",\"files\":" + files + ",\"of\":" + filesOf
                + ",\"err\":\"" + err.replaceAll("[^A-Za-z0-9 .:/_-]", "") + "\"}";
    }

    // ------------------------------------------------------------------ helpers
    static boolean safePath(String p) {
        if (p == null || p.isEmpty() || p.startsWith("/") || p.contains("\\") || p.contains("\0")) return false;
        for (String seg : p.split("/", -1)) if (seg.isEmpty() || seg.equals(".") || seg.equals("..")) return false;
        return true;
    }

    private static HttpURLConnection open(String url) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(15000);
        c.setReadTimeout(30000);
        c.setUseCaches(false);
        c.setInstanceFollowRedirects(true);
        c.setRequestProperty("Cache-Control", "no-cache");
        c.setRequestProperty("User-Agent", "MBC-Legacies-app");
        return c;
    }

    private static byte[] get(String url, int max) throws IOException {
        HttpURLConnection c = open(url);
        try {
            if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode());
            try (InputStream in = c.getInputStream()) {
                ByteArrayOutputStream out = new ByteArrayOutputStream();
                byte[] buf = new byte[16384];
                int r;
                while ((r = in.read(buf)) > 0) {
                    out.write(buf, 0, r);
                    if (out.size() > max) throw new IOException("too big");
                }
                return out.toByteArray();
            }
        } finally {
            c.disconnect();
        }
    }

    static String sha256(File f) throws IOException {
        try (InputStream in = new FileInputStream(f)) {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] buf = new byte[32768];
            int r;
            while ((r = in.read(buf)) > 0) md.update(buf, 0, r);
            return hex(md.digest());
        } catch (java.security.NoSuchAlgorithmException e) {
            throw new IOException(e.getMessage());
        }
    }

    private static String hex(byte[] b) {
        StringBuilder s = new StringBuilder();
        for (byte x : b) s.append(String.format("%02x", x));
        return s.toString();
    }

    private static void copy(File a, File b) throws IOException {
        try (InputStream in = new FileInputStream(a); OutputStream out = new FileOutputStream(b)) {
            byte[] buf = new byte[32768];
            int r;
            while ((r = in.read(buf)) > 0) out.write(buf, 0, r);
        }
    }

    static String readText(File f) {
        try (BufferedReader r = new BufferedReader(new InputStreamReader(new FileInputStream(f), StandardCharsets.UTF_8))) {
            StringBuilder s = new StringBuilder();
            char[] buf = new char[8192];
            int n;
            while ((n = r.read(buf)) > 0) s.append(buf, 0, n);
            return s.toString();
        } catch (IOException e) {
            return "";
        }
    }

    public static String readStream(InputStream in) throws IOException {
        try (InputStream i = in) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[16384];
            int r;
            while ((r = i.read(buf)) > 0) out.write(buf, 0, r);
            return new String(out.toByteArray(), StandardCharsets.UTF_8);
        }
    }

    private static void writeText(File f, String text) throws IOException {
        File tmp = new File(f.getPath() + ".tmp");
        try (OutputStream out = new FileOutputStream(tmp)) {
            out.write(text.getBytes(StandardCharsets.UTF_8));
        }
        if (!tmp.renameTo(f)) {
            f.delete();
            if (!tmp.renameTo(f)) throw new IOException("could not save " + f.getName());
        }
    }

    private int readInt(String name) {
        try {
            return Integer.parseInt(readText(new File(root, name)).trim());
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    private void writeInt(String name, int v) {
        try { writeText(new File(root, name), String.valueOf(v)); } catch (IOException e) { /* tried */ }
    }

    private static void delete(File f) {
        if (f == null || !f.exists()) return;
        File[] kids = f.listFiles();
        if (kids != null) for (File k : kids) delete(k);
        f.delete();
    }
}
