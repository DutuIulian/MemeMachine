package com.example.memesclient;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.widget.Toast;

import com.example.memesclient.activities.MainActivity;

import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.security.cert.CertificateException;

public class MemeRequestTask extends AsyncTask<Void, Void, Meme> {
    private final static int MAX_IMAGE_SIZE = 10 * 1024 * 1024;

    private final MainActivity mainActivity;

    private Bitmap bitmap;
    private String path;
    private ConfigurationManager configurationManager;
    private String errorMessage;

    public MemeRequestTask(MainActivity mainActivity,
                           ConfigurationManager configurationManager) {
        this.configurationManager = configurationManager;
        this.mainActivity = mainActivity;
    }

    @Override
    protected Meme doInBackground(Void... voids) {
        byte[] buffer = new byte[MAX_IMAGE_SIZE];
        Socket socket = null;
        errorMessage = "";

        try {
            if ("On".equals(this.configurationManager.get("ssl"))) {
                MySSLSocketFactory sslSocketFactory
                        = new MySSLSocketFactory(mainActivity.getApplicationContext());
                socket = sslSocketFactory.createSocket(this.configurationManager.get("host"),
                        Integer.parseInt(this.configurationManager.get("port")));
            } else {
                socket = new Socket(this.configurationManager.get("host"),
                        Integer.parseInt(this.configurationManager.get("port")));
            }
            OutputStreamWriter outputStreamWriter = new OutputStreamWriter(socket.getOutputStream());
            InputStream inputStream = socket.getInputStream();

            String passwordHash = this.configurationManager.get("password_hash");
            outputStreamWriter.write("GET_MEME"
                    + CommunicationUtils.convertToLengthValueFormat(passwordHash));
            outputStreamWriter.flush();

            int read = inputStream.read(buffer, 0, MAX_IMAGE_SIZE);
            if (read == -1) {
                errorMessage = "Server error";
                return null;
            }

            if ("WRONG_PASSWORD".equals
                    (new String(buffer, 0, "WRONG_PASSWORD".length(), "UTF-8"))) {
                errorMessage = "Wrong password";
                return null;
            }

            String data = new String(buffer, 0, read, "UTF-8");
            CommunicationUtils.DataOffset dataOffset = CommunicationUtils.parseLengthValue(data, 0);
            path = dataOffset.getData();
            int size = read - dataOffset.getEndOffset();
            System.arraycopy(buffer, dataOffset.getEndOffset(), buffer, 0, size);

            while (true) {
                read = inputStream.read(buffer, size, MAX_IMAGE_SIZE - size);
                if (read == -1) {
                    break;
                }
                size += read;
                if(size >= MAX_IMAGE_SIZE) {
                    break;
                }
            }
            bitmap = BitmapFactory.decodeByteArray(buffer, 0, size);
        } catch (UnknownHostException e) {
            errorMessage = "Unknown host";
            return null;
        } catch (CertificateException e) {
            errorMessage = "Bad certificate";
            return null;
        } catch (Exception e) {
            errorMessage = "Connection problem";
            return null;
        } finally {
            try {
                socket.close();
            } catch (Exception e) {
            }
        }
        return new Meme(path, bitmap);
    }

    @Override
    protected void onPostExecute(Meme result) {
        if (errorMessage.isEmpty()) {
            mainActivity.displayMeme(result);
        } else {
            Toast.makeText(mainActivity,
                    errorMessage,
                    Toast.LENGTH_LONG).show();
        }
        mainActivity.taskFinished();
    }
}
