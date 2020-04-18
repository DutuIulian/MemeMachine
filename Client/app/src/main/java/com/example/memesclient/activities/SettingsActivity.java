package com.example.memesclient.activities;

import android.content.Intent;
import android.os.Bundle;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.Toast;

import androidx.appcompat.app.ActionBar;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NavUtils;

import com.example.memesclient.ConfigurationManager;
import com.example.memesclient.R;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.channels.FileChannel;
import java.security.MessageDigest;

public class SettingsActivity extends AppCompatActivity {
    private final static int PICK_FILE_RESULT_CODE = 1;

    private ConfigurationManager configurationManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        ActionBar actionBar = this.getSupportActionBar();
        if (actionBar != null) {
            actionBar.setDisplayHomeAsUpEnabled(true);
        }

        this.configurationManager = new ConfigurationManager(getFilesDir());
        putValuesIntoEdits();
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        if (id == android.R.id.home) {
            NavUtils.navigateUpFromSameTask(this);
        }
        return super.onOptionsItemSelected(item);
    }

    private void putValuesIntoEdits() {
        EditText host = findViewById(R.id.hostEditText);
        host.setText(this.configurationManager.get("host"));
        EditText port = findViewById(R.id.portEditText);
        port.setText(this.configurationManager.get("port"));
        Switch ssl = findViewById(R.id.sslSwitch);

        if (this.configurationManager.get("ssl") == null) {
            ssl.setChecked(true);
        } else {
            ssl.setChecked(this.configurationManager.get("ssl").equals("On"));
        }
    }

    public void changeCertificate(View v) {
        Intent fileIntent = new Intent(Intent.ACTION_GET_CONTENT);
        fileIntent.addCategory(Intent.CATEGORY_OPENABLE);
        fileIntent.setType("*/*");
        try {
            startActivityForResult(fileIntent, PICK_FILE_RESULT_CODE);
        } catch (Exception e) {
            Toast.makeText(this,
                    "An error occurred",
                    Toast.LENGTH_LONG).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (data != null && requestCode == PICK_FILE_RESULT_CODE && resultCode == RESULT_OK) {
            try {
                ConfigurationManager.copyFile((FileInputStream) getContentResolver().openInputStream(data.getData()),
                        new File(getFilesDir(), ConfigurationManager.CERTIFICATE_FILE_NAME));
                Toast.makeText(this,
                        "Copied certificate successfully",
                        Toast.LENGTH_LONG).show();
            } catch (Exception e) {
                Toast.makeText(this,
                        "Could not copy certificate",
                        Toast.LENGTH_LONG).show();
                e.printStackTrace();
            }
        }
    }

    public void changePassword(View v) {
        EditText passwordEditText = findViewById(R.id.passwordEditText);
        String password = passwordEditText.getText().toString();

        if (password.isEmpty()) {
            Toast.makeText(this,
                    "Password can not be empty",
                    Toast.LENGTH_LONG).show();
            return;
        }

        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] bytes = digest.digest(password.getBytes("UTF-8"));
            StringBuffer passwordHash = new StringBuffer();

            for (int i = 0; i < bytes.length; i++) {
                String hex = Integer.toHexString(0xff & bytes[i]);
                if (hex.length() == 1) {
                    passwordHash.append('0');
                }
                passwordHash.append(hex);
            }

            this.configurationManager.put("password_hash", passwordHash.toString());
            Toast.makeText(this,
                    "The password was set",
                    Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            Toast.makeText(this,
                    "There was a problem saving the password",
                    Toast.LENGTH_LONG).show();
        }
    }

    public void submit(View v) {
        String host = ((EditText) findViewById(R.id.hostEditText)).getText().toString();
        if (host.isEmpty()) {
            Toast.makeText(this,
                    "Input host",
                    Toast.LENGTH_LONG).show();
            return;
        }

        String port = ((EditText) findViewById(R.id.portEditText)).getText().toString();
        try {
            int intPort = Integer.parseInt(port);
            if (intPort <= 0 || intPort > 65535) {
                throw new Exception();
            }
        } catch (Exception e) {
            Toast.makeText(this,
                    "Invalid port",
                    Toast.LENGTH_LONG).show();
            return;
        }

        boolean ssl = ((Switch) findViewById(R.id.sslSwitch)).isChecked();

        if (ssl && !new File(getFilesDir(), ConfigurationManager.CERTIFICATE_FILE_NAME).exists()) {
            Toast.makeText(this,
                    "Select a certificate",
                    Toast.LENGTH_LONG).show();
            return;
        }

        if (configurationManager.get("password_hash") == null) {
            Toast.makeText(this,
                    "Set a password",
                    Toast.LENGTH_LONG).show();
            return;
        }

        configurationManager.put("host", host);
        configurationManager.put("port", port);
        configurationManager.put("ssl", ssl ? "On" : "Off");

        try {
            configurationManager.dump();
            Toast.makeText(this,
                    "Configuration saved",
                    Toast.LENGTH_LONG).show();
        } catch (Exception e) {
            e.printStackTrace();
            Toast.makeText(this,
                    "There was a problem saving the configuration",
                    Toast.LENGTH_LONG).show();
        }
    }
}