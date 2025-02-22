package com.reconstruction;

import com.raylib.Raylib.Vector3;
import java.util.ArrayList;
import java.awt.image.BufferedImage;

@SuppressWarnings("resource")
public class View {

    private String name;
    public ArrayList<Vector3> vertices;
    private Vector3 position;
    public Vector3 vx;
    public Vector3 vy;
    public Vector3 vz;

    public View(String name, BufferedImage image, Vector3 position, Vector3 vx, Vector3 vy, Vector3 vz) {
        this.name = name;
        this.position = position;
        this.vx = vx;
        this.vy = vy;
        this.vz = vz;
        this.vertices = new ArrayList<>();
        extractVerticesFromImage(image);
    }

    private void extractVerticesFromImage(BufferedImage image) {
        final int rows = image.getHeight();
        final int cols  = image.getWidth();
        final int half_rows = rows >> 1;
        final int half_cols = cols >> 1;

        for (int row = 1; row < rows - 1; row++) {
            final int z_rel = half_rows - row;

            for (int col = 1; col < cols - 1; col++) {
                if((image.getRGB(row, col) & 0xff) != 0) {
                    // skip backgrould (white) pixels
                    continue;
                }
            
                // Check if the current 3x3 pixel neighbourhood forms a vertex
                // at the pixel (row, col) by suming its values vertically or 
                // horizontally.

                final int rowv = (image.getRGB(row, col - 1) & 0xff) & (image.getRGB(row, col + 1) & 0xff);
                final int colv = (image.getRGB(row - 1, col) & 0xff) & (image.getRGB(row + 1, col) & 0xff);

                if ((rowv == 0) && (colv == 0)) {
                    // Corner detected (its not a horizontal or vertical line).
                    // Translate (x_rel, z_rel) to (x,y,z) coordinates in space.
                    final int x_rel = col - half_cols;
                    this.vertices.add(this.point3DFromImage(x_rel, z_rel));
                }
            }
        }
    }

    private Vector3 point3DFromImage(int x, int z) {
        return new Vector3()
            .x((x * this.vx.x()) + (z * this.vz.x()) + this.position.x())
            .y((x * this.vx.y()) + (z * this.vz.y()) + this.position.y())
            .z((x * this.vx.z()) + (z * this.vz.z()) + this.position.z());
    }

    @Override
    public String toString() {
        String position = this.position.x() + ", " + this.position.y() + ", " + this.position.z();
        String vx = this.vx.x() + ", " + this.vx.y() + ", " + this.vx.z();
        String vy = this.vy.x() + ", " + this.vy.y() + ", " + this.vy.z();
        String vz = this.vz.x() + ", " + this.vz.y() + ", " + this.vz.z();

        return "[View: " + this.name + "]\n" + 
            "Position: [" + position + "]\n" + 
            "Vx: [" + vx + "]\n" +
            "Vx: [" + vy + "]\n" +
            "Vx: [" + vz + "]\n" + 
            "Vertices: " + vertices.size() + "\n";
    }
}