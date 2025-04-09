package com.util;

public class Segment<T> {

    public T src;
    public T dst;

    public Segment(final T src, final T dst) {
        this.src = src;
        this.dst = dst;
    }
}