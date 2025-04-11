package com.util;

import org.apache.commons.math3.geometry.Vector;

public class Segment<T extends Vector<?>> {

    public final T src;
    public final T dst;

    public Segment(final T src, final T dst) {
        this.src = src;
        this.dst = dst;
    }
}