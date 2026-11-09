package uk.mbc.legacies;

import android.Manifest;
import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.media.AudioDeviceInfo;
import android.media.AudioManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.webkit.WebViewAssetLoader;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

/**
 * MBC Legacies: the whole game is the web page in assets/www, shown full screen in a WebView.
 * The page is served from https://appassets.androidplatform.net so it can fetch its own music and art,
 * and reach the online-play database, like it would on the web.
 */
public class MainActivity extends Activity {
    private static final String HOME = "https://appassets.androidplatform.net/assets/www/index.html";
    // in-app updates (Version 66): the latest release's file list, and where each file is fetched from
    private static final String OTA_LIST = "https://github.com/TimChattawayHEI/MBCLegacy/releases/latest/download/ota.txt";
    private static final String OTA_RAW = "https://raw.githubusercontent.com/TimChattawayHEI/MBCLegacy/";
    private WebView web;
    private Ota ota;
    // Version 84: voice chat. A mic request from the page waiting on Android's own permission prompt
    private static final int ASK_MIC = 84;
    private PermissionRequest micAsk;
    private boolean voiceOn;
    private int callVolBefore = -1;   // Version 84.1: the call volume to put back when voice stops

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        hideBars();

        ota = makeOta();

        web = new WebView(this);
        web.setBackgroundColor(0xFF0C1014);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setTextZoom(100);

        // game files: a downloaded update first (if one is switched in), otherwise the copy inside the APK
        final WebViewAssetLoader.AssetsPathHandler fromApk = new WebViewAssetLoader.AssetsPathHandler(this);
        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", path -> {
                    if (ota != null && path.startsWith("www/")) {
                        String rel = path.substring(4);
                        if (rel.equals("build.json") && ota.build() > 0) {
                            byte[] b = ("{\"build\": " + ota.build() + "}").getBytes(StandardCharsets.UTF_8);
                            return new WebResourceResponse("application/json", "utf-8", new ByteArrayInputStream(b));
                        }
                        File f = ota.resolve(rel);
                        if (f != null) {
                            try { return new WebResourceResponse(mimeOf(rel), null, new FileInputStream(f)); }
                            catch (IOException e) { /* fall back to the APK's copy */ }
                        }
                    }
                    return fromApk.handle(path);
                })
                .build();
        web.addJavascriptInterface(new Native(), "MBCNative");

        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest req) {
                return loader.shouldInterceptRequest(req.getUrl());
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest req) {
                Uri u = req.getUrl();
                if ("appassets.androidplatform.net".equals(u.getHost())) return false;
                // anything else (a link in the credits, say) opens in the phone's browser
                try { startActivity(new Intent(Intent.ACTION_VIEW, u)); } catch (Exception e) { /* no browser */ }
                return true;
            }
        });

        // Version 84: the page may use the microphone (voice chat in online co-op), and nothing else
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest req) {
                boolean mic = false;
                for (String r : req.getResources()) if (PermissionRequest.RESOURCE_AUDIO_CAPTURE.equals(r)) mic = true;
                if (!mic) { req.deny(); return; }
                if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) == PackageManager.PERMISSION_GRANTED) {
                    req.grant(new String[] { PermissionRequest.RESOURCE_AUDIO_CAPTURE });
                    return;
                }
                if (micAsk != null) { try { micAsk.deny(); } catch (Exception e) { /* gone */ } }
                micAsk = req;
                requestPermissions(new String[] { Manifest.permission.RECORD_AUDIO }, ASK_MIC);
            }

            @Override
            public void onPermissionRequestCanceled(PermissionRequest req) {
                if (req == micAsk) micAsk = null;
            }
        });

        if (state != null) web.restoreState(state);
        else web.loadUrl(HOME);
    }

    private Ota makeOta() {
        Ota.Manifest bundled = null;
        try { bundled = Ota.Manifest.parse(Ota.readStream(getAssets().open("www/ota.txt"))); }
        catch (Exception e) { /* an APK without the list: no in-app updates */ }
        Ota o = new Ota(new File(getFilesDir(), "ota"), bundled, OTA_LIST, OTA_RAW);
        try { o.startup(); } catch (Exception e) { return null; }
        return o;
    }

    private static String mimeOf(String p) {
        String e = p.substring(p.lastIndexOf('.') + 1).toLowerCase();
        switch (e) {
            case "html": case "htm": return "text/html";
            case "js": case "mjs": return "text/javascript";
            case "css": return "text/css";
            case "json": return "application/json";
            case "png": return "image/png";
            case "jpg": case "jpeg": return "image/jpeg";
            case "gif": return "image/gif";
            case "webp": return "image/webp";
            case "svg": return "image/svg+xml";
            case "ogg": case "oga": return "audio/ogg";
            case "mp3": return "audio/mpeg";
            case "wav": return "audio/wav";
            case "m4a": return "audio/mp4";
            case "woff": return "font/woff";
            case "woff2": return "font/woff2";
            case "ttf": return "font/ttf";
            case "txt": return "text/plain";
            default: return "application/octet-stream";
        }
    }

    /** What the page can ask the app about updates (window.MBCNative). */
    private final class Native {
        @JavascriptInterface public String otaStatus() { return ota == null ? "{\"state\":\"off\"}" : ota.statusJson(); }
        @JavascriptInterface public void otaCheck() { if (ota != null) ota.checkAsync(); }
        /** Switch to the downloaded update and reload the game. */
        @JavascriptInterface public boolean otaApply() {
            if (ota == null || !ota.apply()) return false;
            runOnUiThread(() -> { if (web != null) web.loadUrl(HOME); });
            return true;
        }
        /** Version 84: this app can do voice chat (older APKs have no mic permission). */
        @JavascriptInterface public boolean canVoice() { return true; }
        /** Version 84: voice is live (or not): keep the sound on the loudspeaker while it is. */
        @JavascriptInterface public void voice(final boolean on) { runOnUiThread(() -> voiceRoute(on)); }
    }

    @Override
    public void onRequestPermissionsResult(int code, String[] perms, int[] res) {
        super.onRequestPermissionsResult(code, perms, res);
        if (code != ASK_MIC || micAsk == null) return;
        PermissionRequest r = micAsk; micAsk = null;
        boolean ok = res.length > 0 && res[0] == PackageManager.PERMISSION_GRANTED;
        try {
            if (ok) r.grant(new String[] { PermissionRequest.RESOURCE_AUDIO_CAPTURE });
            else r.deny();
        } catch (Exception e) { /* the page stopped asking */ }
    }

    /**
     * When a phone opens its mic for a call, Android switches to call mode, which on some phones quietens the game
     * or sends it to the earpiece. While voice is live, sound goes to the loudspeaker (unless headphones are in)
     * and the volume buttons work on what's playing. Back to normal after.
     */
    @SuppressWarnings("deprecation")
    private void voiceRoute(boolean on) {
        AudioManager am = (AudioManager) getSystemService(Context.AUDIO_SERVICE);
        if (am == null || on == voiceOn) return;
        voiceOn = on;
        try {
            if (on) {
                am.setMode(AudioManager.MODE_IN_COMMUNICATION);
                if (!headphonesIn(am)) {
                    if (Build.VERSION.SDK_INT >= 31) {
                        for (AudioDeviceInfo d : am.getAvailableCommunicationDevices())
                            if (d.getType() == AudioDeviceInfo.TYPE_BUILTIN_SPEAKER) { am.setCommunicationDevice(d); break; }
                    } else am.setSpeakerphoneOn(true);
                }
                setVolumeControlStream(AudioManager.STREAM_VOICE_CALL);
                // Version 84.1 (Tim: "very quiet"): with the mic open the phone plays everything at call volume,
                // which is often left low. Bring it up to at least where the media volume is, and put it back after
                int cMax = am.getStreamMaxVolume(AudioManager.STREAM_VOICE_CALL), mMax = am.getStreamMaxVolume(AudioManager.STREAM_MUSIC);
                int cNow = am.getStreamVolume(AudioManager.STREAM_VOICE_CALL), mNow = am.getStreamVolume(AudioManager.STREAM_MUSIC);
                int want = mMax > 0 ? (int) Math.ceil((double) cMax * mNow / mMax) : cNow;
                if (want > cNow) { callVolBefore = cNow; am.setStreamVolume(AudioManager.STREAM_VOICE_CALL, Math.min(cMax, want), 0); }
                else callVolBefore = -1;
            } else {
                if (callVolBefore >= 0) { am.setStreamVolume(AudioManager.STREAM_VOICE_CALL, callVolBefore, 0); callVolBefore = -1; }
                if (Build.VERSION.SDK_INT >= 31) am.clearCommunicationDevice(); else am.setSpeakerphoneOn(false);
                am.setMode(AudioManager.MODE_NORMAL);
                setVolumeControlStream(AudioManager.USE_DEFAULT_STREAM_TYPE);
            }
        } catch (Exception e) { /* leave the phone as it is */ }
    }

    private static boolean headphonesIn(AudioManager am) {
        for (AudioDeviceInfo d : am.getDevices(AudioManager.GET_DEVICES_OUTPUTS)) {
            int t = d.getType();
            if (t == AudioDeviceInfo.TYPE_WIRED_HEADSET || t == AudioDeviceInfo.TYPE_WIRED_HEADPHONES || t == AudioDeviceInfo.TYPE_USB_HEADSET
                    || t == AudioDeviceInfo.TYPE_BLUETOOTH_SCO || t == AudioDeviceInfo.TYPE_BLUETOOTH_A2DP
                    || (Build.VERSION.SDK_INT >= 31 && t == AudioDeviceInfo.TYPE_BLE_HEADSET)) return true;
        }
        return false;
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        if (web != null) web.saveState(out);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideBars();
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (web != null) { web.evaluateJavascript("window.__voicePause && window.__voicePause()", null); web.onPause(); }
        voiceRoute(false);   // the page turns the mic off when it's hidden, and back on (and asks for the speaker again) when it's back
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) { web.onResume(); web.evaluateJavascript("window.__voiceResume && window.__voiceResume()", null); }
        hideBars();
    }

    @Override
    public void onBackPressed() {
        // the back button pauses the game (the page decides); a second press from the pause menu leaves
        if (web != null) {
            web.evaluateJavascript("(window.__appBack && window.__appBack()) ? 1 : 0", v -> {
                if (!"1".equals(v)) MainActivity.super.onBackPressed();
            });
        } else super.onBackPressed();
    }

    @SuppressWarnings("deprecation")
    private void hideBars() {
        View d = getWindow().getDecorView();
        d.setSystemUiVisibility(View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN);
    }
}
