package com.example.memesclient;

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

    public Bitmap getBitmap() {
        return bitmap;
    }
}
