package com.reconstruction;

import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.yaml.Vector3DYaml;
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

    public View() { 
        this.vertices = new ArrayList<>(); 
    }

    public void extractVerticesFromImage(final BufferedImage image) {
        final int rows = image.getHeight();
        final int cols  = image.getWidth();
        final int z0 = rows >> 1;
        final int x0 = cols >> 1;

        for (int zi = 1; zi < rows - 1; ++zi) {
            final int z_rel = z0 - zi;

            for (int xi = 1; xi < cols - 1; ++xi) {
                if((image.getRGB(xi, zi) & 0xff) != 0) {
                    // skip backgrould (white) pixels
                    continue;
                }

                // Check if the current 3x3 pixel neighbourhood forms a vertex at the pixel (xi, zi).
                final int rowv = (image.getRGB(xi, zi - 1) & 0xff) & (image.getRGB(xi, zi + 1) & 0xff);
                final int colv = (image.getRGB(xi - 1, zi) & 0xff) & (image.getRGB(xi + 1, zi) & 0xff);

                if ((rowv == 0) && (colv == 0)) {
                    // Corner detected. The 3x3 pixel neighbourhood its not a horizontal or vertical line
                    // nor a isolated pixel). Translate (x_rel, z_rel) to (x,y,z) coordinates in space.
                    final int x_rel = xi - x0;
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

    public ArrayList<Vector3D> getVertices() { return this.vertices; }
    public Vector3D getPosition() { return this.position; }
    public String getName() { return this.name; }
    public Vector3D getVx() { return this.vx; }
    public Vector3D getVy() { return this.vy; }
    public Vector3D getVz() { return this.vz; }

    

    @Override
    public String toString() {
        return "[View: " + this.name + "]\n" + 
            "Position: " + this.position + "\n" + 
            "Vx: " + this.vx + "\n" +
            "Vy: " + this.vy + "\n" +
            "Vz: " + this.vz + "\n" + 
            "Vertices: " + this.vertices.size() + "\n";
    }
}