package com.util;

import java.util.ArrayList;
import org.apache.commons.math3.geometry.Vector;

public class Polygon<T extends Vector<?>> {

    public final ArrayList<Segment<T>> edges;
    public final ArrayList<T> points;

    public Polygon(final ArrayList<T> points) {
        // The edges will be generated later.
        this.points = points;
        this.edges = new ArrayList<>();
    }

    public void generateEdges() {}
}