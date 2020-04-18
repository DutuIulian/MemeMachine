package com.example.memesclient;

import android.util.Log;

public class CommunicationUtils {
    static class DataOffset {
        private String data;
        private int endOffset;

        public DataOffset(String data, int endOffset) {
            this.data = data;
            this.endOffset = endOffset;
        }

        public String getData() {
            return data;
        }

        public int getEndOffset() {
            return endOffset;
        }
    }

    static DataOffset parseLengthValue(String data, int offset) {
        data = data.substring(offset);
        final int length = data.charAt(0) * 256 + data.charAt(1);
        return new DataOffset(data.substring(2, length + 2), offset + length + 2);
    }

    static String convertToLengthValueFormat(String data) {
        final byte[] dataLength = new byte[]{
                (byte) ((data.length() >> 8) & 0xFF),
                (byte) (data.length() & 0xFF)
        };

        try {
            return new String(dataLength, 0, 2, "UTF-8") + data;
        } catch (Exception e) {
            return null;
        }
    }
}
