package com.util;

import java.util.ArrayList;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;

public class Polygon {

    public ArrayList<Vector3D> vertices;
    public ArrayList<Segment<Vector3D>> edges;

    public Polygon(ArrayList<Vector3D> vertices, ArrayList<Segment<Vector3D>> edges) {
        this.vertices = vertices;
        this.edges = edges;
    }
}