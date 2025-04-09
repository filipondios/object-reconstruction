package com.core;

import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import com.google.gson.Gson;

public class ViewCamera {

    public Vector3D position;
    public Vector3D vx;
    public Vector3D vy;
    public Vector3D vz;
    public String name;

    private ViewCamera() {}

    public static ViewCamera deserializeFrom(final String path) throws IOException {
        final Reader jsonReader = new FileReader(path);
        ViewCamera camera = (new Gson()).fromJson(jsonReader, ViewCamera.class);
        jsonReader.close();
        return camera;
    }
}