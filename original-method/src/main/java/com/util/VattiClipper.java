package com.util;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.Set;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;

public final class VattiClipper {

    public static Polygon<Vector2D> clip(final Polygon<Vector2D> subject, final Polygon<Vector2D> clip) {
        if (subject.points.isEmpty() || clip.points.isEmpty()) {
            return new Polygon<Vector2D>(new ArrayList<>());
        }

        final ArrayList<Segment<Vector2D>> subjectEdges = createEdges(subject);
        final ArrayList<Segment<Vector2D>> clipEdges = createEdges(clip);
        final ArrayList<Vector2D> intersections = findIntersections(subjectEdges, clipEdges);

        // Find vertices of subject that are inside clip polygon
        final ArrayList<Vector2D> subjectVerticesInside = new ArrayList<>();
        for (final Vector2D vertex : subject.points) {
            if (isPointInsidePolygon(vertex, clip)) {
                subjectVerticesInside.add(vertex);
            }
        }

        // Find vertices of clip that are inside subject polygon
        final ArrayList<Vector2D> clipVerticesInside = new ArrayList<>();
        for (final Vector2D vertex : clip.points) {
            if (isPointInsidePolygon(vertex, subject)) {
                clipVerticesInside.add(vertex);
            }
        }

        // Combine all points: intersections and vertices inside
        final Set<Vector2D> uniquePoints = new LinkedHashSet<>();
        uniquePoints.addAll(intersections);
        uniquePoints.addAll(subjectVerticesInside);
        uniquePoints.addAll(clipVerticesInside);       
        return new Polygon<Vector2D>(sortClockwise(new ArrayList<>(uniquePoints)));
    }
    
    private static ArrayList<Segment<Vector2D>> createEdges(final Polygon<Vector2D> polygon) {
        final ArrayList<Segment<Vector2D>> edges = new ArrayList<>();
        final int size = polygon.points.size();
        
        for (int i = 0; i < size; i++) {
            final Vector2D start = polygon.points.get(i);
            final Vector2D end = polygon.points.get((i + 1) % size);
            edges.add(new Segment<Vector2D>(start, end));
        }
        return edges;
    }

    private static ArrayList<Vector2D> findIntersections(
        final ArrayList<Segment<Vector2D>> subjectEdges, 
        final ArrayList<Segment<Vector2D>> clipEdges) {

        final ArrayList<Vector2D> intersections = new ArrayList<>();
        
        for (final Segment<Vector2D> subjectEdge : subjectEdges) {
            for (final Segment<Vector2D> clipEdge : clipEdges) {
                final Vector2D intersection = computeIntersection(
                    subjectEdge.src, subjectEdge.dst,
                    clipEdge.src, clipEdge.dst
                );
                
                if (intersection != null && 
                    !intersection.equals(new Vector2D(Double.MAX_VALUE, Double.MAX_VALUE))) {
                    intersections.add(intersection);
                }
            }
        }
        return intersections;
    }
    
    private static Vector2D computeIntersection(
        final Vector2D a1, final Vector2D a2,
        final Vector2D b1, final Vector2D b2) {
        
        final double aDiffX = a2.getX() - a1.getX();
        final double aDiffY = a2.getY() - a1.getY();
        final double bDiffX = b2.getX() - b1.getX();
        final double bDiffY = b2.getY() - b1.getY();
        final double denominator = aDiffX * bDiffY - aDiffY * bDiffX;
        
        if (denominator == 0) {
            return new Vector2D(Double.MAX_VALUE, Double.MAX_VALUE);
        }
        
        final double c1 = aDiffX * a1.getY() - aDiffY * a1.getX();
        final double c2 = bDiffX * b1.getY() - bDiffY * b1.getX();
        final double x = (bDiffX * c1 - aDiffX * c2) / denominator;
        final double y = (bDiffY * c1 - aDiffY * c2) / denominator;
        
        // Check if the intersection point lies within both line segments
        if (isPointOnSegment(a1, a2, new Vector2D(x, y)) &&
            isPointOnSegment(b1, b2, new Vector2D(x, y))) {
            return new Vector2D(x, y);
        }
        
        return new Vector2D(Double.MAX_VALUE, Double.MAX_VALUE);
    }
    
    private static boolean isPointOnSegment(
        final Vector2D start, 
        final Vector2D end, 
        final Vector2D point) {
        
        final double minX = Math.min(start.getX(), end.getX());
        final double maxX = Math.max(start.getX(), end.getX());
        final double minY = Math.min(start.getY(), end.getY());
        final double maxY = Math.max(start.getY(), end.getY());
        
        return point.getX() >= minX && point.getX() <= maxX &&
               point.getY() >= minY && point.getY() <= maxY;
    }
    
    private static boolean isPointInsidePolygon(
        final Vector2D point, 
        final Polygon<Vector2D> polygon) {
        
        final int n = polygon.points.size();
        boolean inside = false;
        
        for (int i = 0, j = n - 1; i < n; j = i++) {
            final Vector2D p1 = polygon.points.get(i);
            final Vector2D p2 = polygon.points.get(j);
            
            if (((p1.getY() > point.getY()) != (p2.getY() > point.getY())) &&
                (point.getX() < (p2.getX() - p1.getX()) * (point.getY() - p1.getY()) / 
                (p2.getY() - p1.getY()) + p1.getX())) {
                inside = !inside;
            }
        }
        return inside;
    }

    private static ArrayList<Vector2D> sortClockwise(final ArrayList<Vector2D> points) {
        if (points.size() <= 2) {
            return points;
        }

        // Find the centroid
        double centerX = 0;
        double centerY = 0;
        for (final Vector2D point : points) {
            centerX += point.getX();
            centerY += point.getY();
        }
        centerX /= points.size();
        centerY /= points.size();

        // Sort points based on their angle relative to the centroid
        final Vector2D center = new Vector2D(centerX, centerY);
        points.sort((a, b) -> {
            double angleA = Math.atan2(a.getY() - center.getY(), a.getX() - center.getX());
            double angleB = Math.atan2(b.getY() - center.getY(), b.getX() - center.getX());
            return Double.compare(angleB, angleA);
        });
        return points;
    }
} 