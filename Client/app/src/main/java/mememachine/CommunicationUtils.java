package mememachine;

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

    static int convertSignedByte(byte b) {
        int i = b;

        if (i < 0) {
            i += 256;
        }

        return i;
    }

    static DataOffset parseLengthValue(byte[] data, int offset) {
        final int length = convertSignedByte(data[offset]) * 256
                + convertSignedByte(data[offset + 1]);

        return new DataOffset(new String(data, offset + 2, length),
                offset + length + 2);
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
