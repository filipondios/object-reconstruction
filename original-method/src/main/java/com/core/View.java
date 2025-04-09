package com.core;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import javax.imageio.ImageIO;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;

import com.util.Images;
import com.util.Segment;

public class View {

    public BufferedImage projection;
    public ViewCamera camera;
    public ArrayList<Segment<Vector2D>> edges;
    public ArrayList<Vector2D> vertices;

    public View(final String path) {
        try {
            this.projection = ImageIO.read(new File(path + "/plane.bmp"));
            this.projection = Images.getImageCountour(this.projection);
            this.camera = ViewCamera.deserializeFrom(path + "/camera.json");
            this.vertices = new ArrayList<>();
            this.vertices = new ArrayList<>();
        } catch (IOException e) {
            e.printStackTrace();
            System.exit(-1);
        }
    }

    public static boolean isViewDir(final String path) {
        return (new File(path + "/camera.json").isFile())
            && (new File(path + "/plane.bmp").isFile());
    }

    @Override
    public String toString() {
        return this.camera.name;
    }
}