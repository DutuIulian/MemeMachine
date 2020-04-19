package mememachine;

import android.graphics.Bitmap;

public class Meme {
    private String path;
    private Bitmap bitmap;

    public Meme(String path, Bitmap bitmap) {
        this.path = path;
        this.bitmap = bitmap;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public Bitmap getBitmap() {
        return bitmap;
    }
}
