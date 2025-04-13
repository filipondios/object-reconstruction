package com.util;

import java.util.ArrayList;
import org.apache.commons.math3.geometry.Vector;

public class Polygon<T extends Vector<?>> {

    public final ArrayList<T> points;

    public Polygon(final ArrayList<T> points) {
        // This class its not really a polygon, but a
        // polygonal line.
        this.points = points;
    }
}