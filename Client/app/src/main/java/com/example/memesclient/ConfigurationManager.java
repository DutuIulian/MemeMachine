package com.example.memesclient;

import android.util.Log;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.channels.FileChannel;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.StringTokenizer;

public class ConfigurationManager {
    private HashMap<String, String> hashMap;
    private File filesDir;

    private final static String CONFIGURATION_FILE_NAME = "configuration.ini";

    public final static String CERTIFICATE_FILE_NAME = "certificate.crt";
    ;

    public ConfigurationManager(File filesDir) {
        this.hashMap = new HashMap<>();
        this.filesDir = filesDir;
        try {
            load();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void load() throws IOException {
        BufferedReader bfr = new BufferedReader(
                new FileReader(new File(this.filesDir, CONFIGURATION_FILE_NAME)));
        String line;

        while ((line = bfr.readLine()) != null) {
            StringTokenizer strTok = new StringTokenizer(line, "=");
            String key = strTok.nextToken();
            String value = strTok.nextToken();
            hashMap.put(key, value);
        }

        bfr.close();
    }

    public void dump() throws IOException {
        File f = new File(this.filesDir, CONFIGURATION_FILE_NAME);
        if (!f.exists()) {
            f.createNewFile();
        }

        PrintWriter prw = new PrintWriter(new FileWriter(f));
        Iterator<Map.Entry<String, String>> it = hashMap.entrySet().iterator();
        do {
            Map.Entry<String, String> entry = it.next();
            prw.println(entry.getKey() + "=" + entry.getValue());
        } while (it.hasNext());

        prw.close();
    }

    public boolean areSettingsValid() {
        return get("host") != null && get("port") != null && get("password_hash") != null
                && (get("ssl").equals("Off") || new File(filesDir, CERTIFICATE_FILE_NAME).exists());
    }

    public void put(String key, String value) {
        hashMap.put(key, value);
    }

    public String get(String key) {
        return hashMap.get(key);
    }

    public static void copyFile(FileInputStream srcFile, File destFile) throws IOException {
        if (!destFile.exists()) {
            destFile.createNewFile();
        }

        FileChannel source = null;
        FileChannel destination = null;

        try {
            source = srcFile.getChannel();
            destination = new FileOutputStream(destFile).getChannel();
            destination.transferFrom(source, 0, source.size());
        } finally {
            if (source != null) {
                source.close();
            }
            if (destination != null) {
                destination.close();
            }
        }
    }
}
