package uk.mbc.legacies;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
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
        if (web != null) web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (web != null) web.onResume();
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
