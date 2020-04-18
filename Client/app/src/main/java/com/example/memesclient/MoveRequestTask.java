package com.example.memesclient;

import android.os.AsyncTask;
import android.widget.Toast;

import com.example.memesclient.activities.MainActivity;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.security.cert.CertificateException;

public class MoveRequestTask extends AsyncTask<Void, Void, String> {
    private MainActivity mainActivity;
    private ConfigurationManager configurationManager;
    private String currentFilePath;
    private String newFileLocation;

    public MoveRequestTask(MainActivity mainActivity,
                           ConfigurationManager configurationManager,
                           String currentFilePath, final String newFileLocation) {
        this.mainActivity = mainActivity;
        this.configurationManager = configurationManager;
        this.currentFilePath = currentFilePath;
        this.newFileLocation = newFileLocation;
        int index = currentFilePath.lastIndexOf("/");
        if (index < 0) {
            index = currentFilePath.lastIndexOf("\\");
        }
        final String currentFileDirectory = currentFilePath.substring(0, index + 1);
        this.newFileLocation = currentFileDirectory + newFileLocation;
    }

    @Override
    protected String doInBackground(Void... voids) {
        OutputStreamWriter outputStreamWriter;
        BufferedReader bufferedReader;
        Socket socket = null;

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
            outputStreamWriter = new OutputStreamWriter(socket.getOutputStream());
            bufferedReader = new BufferedReader(
                    new InputStreamReader(socket.getInputStream(), "UTF-8"));

            String passwordHash = this.configurationManager.get("password_hash");
            outputStreamWriter.write("MOVE_FILE"
                    + CommunicationUtils.convertToLengthValueFormat(passwordHash)
                    + CommunicationUtils.convertToLengthValueFormat(this.currentFilePath)
                    + CommunicationUtils.convertToLengthValueFormat(this.newFileLocation));
            outputStreamWriter.flush();
            String response = bufferedReader.readLine();

            if ("WRONG_PASSWORD".equals(response)) {
                return "Wrong password";
            }

            if (response.equals("OK")) {
                return "File moved";
            }

            return "Could not move file";
        } catch (UnknownHostException e) {
            return "Unknown host";
        } catch (CertificateException e) {
            return "Bad certificate";
        } catch (Exception e) {
            return "Connection problem";
        } finally {
            if (socket != null) {
                try {
                    socket.close();
                } catch (Exception e) {
                }
            }
        }
    }

    @Override
    protected void onPostExecute(String result) {
        Toast.makeText(mainActivity.getApplicationContext(), result, Toast.LENGTH_LONG).show();
        mainActivity.taskFinished();
    }
}
