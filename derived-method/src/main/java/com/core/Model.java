package com.core;

import java.io.File;
import java.io.FileReader;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.Iterator;
import javax.imageio.ImageIO;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.util.Pair;
import com.google.gson.Gson;
import com.image.ImageProcessing;


public class Model {

    public ArrayList<View> views;
    public HashSet<Vector3D> vertices;
    public ArrayList<Pair<Vector3D, Vector3D>> edges;
    private String name;

    public Model(String name) throws Exception {
        this.views = new ArrayList<>();
        this.vertices = new HashSet<>();
        this.edges = new ArrayList<>();
        this.name = name;

        // A model consists of subdirectories. Each subdirectory stores the
        // information of a different view. Each view consists of the files
        // camera.json and plane.bmp.

        for (File file : (new File("../models/" + name)).listFiles()) {
            if(file.isDirectory()) {
                final String view_camera = file.getCanonicalPath() + "/camera.json";
                final String view_plane  = file.getCanonicalPath() + "/plane.bmp"; 

                // Load the camera position and orientation vectors.
                final Reader json_reader = new FileReader(view_camera);
                View view = (new Gson()).fromJson(json_reader, View.class);
                json_reader.close();

                // Load the view projection plane (BMP) image.
                view.setViewPlane(ImageIO.read(new File(view_plane)));
                this.views.add(view);
            }
        }

        // Sorting the views from highest to lowest number of vertices increases
        // the likelihood of intersection between vertices from different views, 
        // leading to better results in both the initial and refinement stages.

        Collections.sort(this.views, new Comparator<View>() {
            @Override
            public int compare(View v1, View v2) {
                final int v1_vertices = v1.vertices.size();
                final int v2_vertices = v2.vertices.size();
                return Integer.compare(v2_vertices, v1_vertices);
            }
        });
    }

    public void generateInitialReconstruction() {
        // TODO Check for parallel vy vectors
        final View view1 = this.views.get(0);
        final View view2 = this.views.get(1);

        for (final Vector3D v1 : view1.vertices) {
            final Line line1 = new Line(v1, v1.add(view1.vy), 0.0001);

            for (final Vector3D v2 : view2.vertices) {
                // Check if the line which has direction 'view0.vy' and passes
                // through 'p1' intersects with the line which has direction 
                // 'view1.vy' and passes through 'p2'.

                final Line line2 = new Line(v2, v2.add(view2.vy), 0.0001);
                final Vector3D intersection = line1.intersection(line2);

                if (intersection != null) {
                    this.vertices.add(intersection);
                }
            }
        }
    }

    public void refineModelVertices() {
        final Iterator<Vector3D> iterator = this.vertices.iterator();

        while (iterator.hasNext()) {
            Vector3D vertex = iterator.next();

            for (View view : this.views) {
                Vector2D projection = view.realToPlanePoint(vertex);
                projection = view.planeToImageCoord(projection);

                final int x = (int) projection.getX();
                final int z = (int) projection.getY();
                final int pixel_value = view.plane.getRGB(x, z) & 0xff;

                if(pixel_value == ImageProcessing.PIXEL_BACKGROUND) {
                    iterator.remove();
                    break;
                }
            }
        }
    }

    public void generateEdges() {

        // We will try to generate a edge in each axis direction (X,Y,Z) for each
        // vertex in the model. Edges are formed between two vertices in a same axis
        // direction (and line) that have the minimum distance between each other.
        // This cant work with models with gaps.

        final Vector3D x_axis = new Vector3D(1, 0, 0);
        final Vector3D y_axis = new Vector3D(0, 1, 0);
        final Vector3D z_axis = new Vector3D(0, 0, 1);

        for (Vector3D vertex : vertices) {
            // Crear líneas en las tres direcciones principales desde el vértice actual
            final Line x_line = new Line(vertex, vertex.add(x_axis), 0.0001);
            final Line y_line = new Line(vertex, vertex.add(y_axis), 0.0001);
            final Line z_line = new Line(vertex, vertex.add(z_axis), 0.0001);
            
            Vector3D minX = null;
            Vector3D minY = null;
            Vector3D minZ = null;
            
            for (Vector3D other : vertices) {
                if (vertex.equals(other)) continue;
                
                if (x_line.contains(other)) {
                    if (other.getX() > vertex.getX() && 
                        (minX == null || other.getX() < minX.getX())) {
                        minX = other;
                    }
                }
                
                if (y_line.contains(other)) {
                    if (other.getY() > vertex.getY() && 
                        (minY == null || other.getY() < minY.getY())) {
                        minY = other;
                    }
                }

                if (z_line.contains(other)) {
                    if (other.getZ() > vertex.getZ() && 
                        (minZ == null || other.getZ() < minZ.getZ())) {
                        minZ = other;
                    }
                }
            }

            if (minX != null) this.edges.add(new Pair<>(vertex, minX));
            if (minY != null) this.edges.add(new Pair<>(vertex, minY));
            if (minZ != null) this.edges.add(new Pair<>(vertex, minZ));
        }
    }
   
    @Override
    public String toString() {
        String out = "[Model '" + this.name + "']\n";
        for (View view : this.views) { out += view + "\n"; }
        return out;
    }
}