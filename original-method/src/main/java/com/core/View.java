package com.core;

import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import javax.imageio.ImageIO;
import org.apache.commons.lang3.tuple.Pair;
import com.google.gson.Gson;
import com.raylib.Raylib.Vector2;

public class View {

    public BufferedImage projection;
    public ViewCamera camera;
    public ArrayList<Vector2> vertices;
    public ArrayList<Pair<Vector2, Vector2>> edges;

    public View(final String path, final Gson gson) throws IOException {
        this.projection = ImageIO.read(new File(path + "/plane.bmp"));
        this.camera = ViewCamera.deserializeFrom(path + "/camera.json", gson);
        this.vertices = new ArrayList<>();
        this.vertices = new ArrayList<>();
    }

    public static boolean isViewDir(final String path) {
        return (new File(path + "/camera.json").isFile())
            && (new File(path + "/plane.bmp").isFile());
    }
}