package com.reconstruction;

import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.other.Vector3DYaml;
import java.util.ArrayList;
import java.awt.image.BufferedImage;

public class View {

    public String name;
    @JsonDeserialize(using = Vector3DYaml.class)
    private Vector3D position;
    @JsonDeserialize(using = Vector3DYaml.class)
    private Vector3D vx;
    @JsonDeserialize(using = Vector3DYaml.class)
    private Vector3D vy;
    @JsonDeserialize(using = Vector3DYaml.class)
    private Vector3D vz;

    @JsonIgnore
    private ArrayList<Vector3D> vertices;
    public View() { this.vertices = new ArrayList<>(); }

    public void extractVerticesFromImage(BufferedImage image) {
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

    private Vector3D point3DFromImage(int x, int z) {
        return new Vector3D(
            (x * this.vx.getX()) + (z * this.vz.getX()) + this.position.getX(),
            (x * this.vx.getY()) + (z * this.vz.getY()) + this.position.getY(),
            (x * this.vx.getZ()) + (z * this.vz.getZ()) + this.position.getZ()
        );
    }

    public void setName(String name) { this.name = name; }
    public void setPosition(Vector3D position) { this.position = position; }
    public void setVx(Vector3D vx) { this.vx = vx; }
    public void setVy(Vector3D vy) { this.vy = vy; }
    public void setVz(Vector3D vz) { this.vz = vz; }

    public String getName() { return this.name; }
    public Vector3D getPosition() { return this.position; }
    public Vector3D getVx() { return this.vx; }
    public Vector3D getVy() { return this.vy; }
    public Vector3D getVz() { return this.vz; }
    public ArrayList<Vector3D> getVertices() { return this.vertices; }

    @Override
    public String toString() {
        return "[View: " + this.name + "]\n" + 
            "Position: " + this.position + "\n" + 
            "Vx: " + this.vx + "\n" +
            "Vx: " + this.vy + "\n" +
            "Vx: " + this.vz + "\n" + 
            "Vertices: " + this.vertices.size() + "\n";
    }
}