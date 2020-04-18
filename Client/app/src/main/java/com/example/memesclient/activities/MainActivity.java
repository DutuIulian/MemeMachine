package com.example.memesclient.activities;

import android.Manifest;
import android.app.AlertDialog;
import android.content.ContentResolver;
import android.content.ContentValues;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.MediaStore;
import android.text.InputType;
import android.view.Gravity;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import com.example.memesclient.ConfigurationManager;
import com.example.memesclient.Meme;
import com.example.memesclient.MemeRequestTask;
import com.example.memesclient.MoveRequestTask;
import com.example.memesclient.R;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.List;

public class MainActivity extends AppCompatActivity {
    private final static int MAX_LIST_SIZE = 16;
    private final static int REQUEST_EXTERNAL_STORAGE = 1;
    private final static String[] PERMISSIONS_STORAGE = {
            Manifest.permission.READ_EXTERNAL_STORAGE,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
    };

    private List<Meme> memes = new ArrayList<>(MAX_LIST_SIZE);
    private ConfigurationManager configurationManager = null;
    private Uri uri = null;
    private String newFileLocation = null;
    private boolean taskRunning = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        int permission = ActivityCompat.checkSelfPermission(
                this, Manifest.permission.WRITE_EXTERNAL_STORAGE);
        if (permission != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this,
                    PERMISSIONS_STORAGE, REQUEST_EXTERNAL_STORAGE);
        }

        this.configurationManager = new ConfigurationManager(getFilesDir());
        startMemeRequestTask(findViewById(android.R.id.content).getRootView());
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater menuInflater = getMenuInflater();
        menuInflater.inflate(R.menu.settings_menu, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();
        if (id == R.id.action_settings) {
            Intent intent = new Intent(MainActivity.this, SettingsActivity.class);
            startActivity(intent);
            return true;
        }
        return super.onOptionsItemSelected(item);
    }

    public void startMemeRequestTask(View v) {
        if (taskRunning) {
            return;
        }

        try {
            this.configurationManager.load();
            if (!this.configurationManager.areSettingsValid()) {
                throw new Exception();
            }
        } catch (Exception e) {
            Toast.makeText(this,
                    "The configuration is invalid.\n Please change it.",
                    Toast.LENGTH_LONG).show();
            return;
        }

        taskRunning = true;
        MemeRequestTask memeRequestTask = new MemeRequestTask(
                this, this.configurationManager);
        memeRequestTask.execute();
    }

    public void displayMeme(final Meme meme) {
        if (meme == null) {
            return;
        }

        if (memes.size() == MAX_LIST_SIZE) {
            memes.remove(0);
        }

        this.memes.add(meme);
        ImageView imageView = findViewById(R.id.imageViewId);
        imageView.setImageBitmap(meme.getBitmap());
        TextView textView = findViewById(R.id.textViewId);
        textView.setText(meme.getPath());
    }

    public void shareMeme(View v) {
        if (!memes.isEmpty()) {
            Meme meme = memes.get(memes.size() - 1);
            String path = MediaStore.Images.Media.insertImage(
                    getContentResolver(),
                    meme.getBitmap(), "tmp.bmp", ""
            );
            uri = Uri.parse(path);
            Intent intent = new Intent(Intent.ACTION_SEND);
            intent.setType("image/bmp");
            intent.putExtra(Intent.EXTRA_STREAM, uri);
            startActivityForResult(Intent.createChooser(intent, "Share Image"), 0);
        } else {
            Toast.makeText(this,
                    "No image to share",
                    Toast.LENGTH_LONG
            ).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        switch (requestCode) {
            case 0:
                getContentResolver().delete(uri, null, null);
                break;
        }
    }

    public void goBack(View v) {
        if (memes.size() > 1) {
            memes.remove(memes.size() - 1);
            ImageView mImageView = findViewById(R.id.imageViewId);
            mImageView.setImageBitmap(memes.get(memes.size() - 1).getBitmap());
        }
    }

    public void startMoveRequestTask(View v) {
        if (taskRunning) {
            return;
        }

        try {
            this.configurationManager.load();
            if (!this.configurationManager.areSettingsValid()) {
                throw new Exception();
            }
        } catch (Exception e) {
            Toast.makeText(this,
                    "The configuration is invalid.\n Please change it.",
                    Toast.LENGTH_LONG
            ).show();
            return;
        }

        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        TextView title = new TextView(this);
        title.setText("Enter new location");
        title.setGravity(Gravity.CENTER);
        title.setPadding(10, 10, 10, 10);
        title.setTextSize(20);
        builder.setCustomTitle(title);

        final EditText input = new EditText(this);
        input.setInputType(InputType.TYPE_CLASS_TEXT);
        builder.setView(input);

        builder.setPositiveButton("OK", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                newFileLocation = input.getText().toString();
                taskRunning = true;
                new MoveRequestTask(
                        MainActivity.this, configurationManager,
                        memes.get(memes.size() - 1).getPath(), newFileLocation
                ).execute();
            }
        });
        builder.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.cancel();
            }
        });

        builder.show();
    }

    public void taskFinished() {
        taskRunning = false;
    }
}
