package com.core;

import java.io.File;
import java.io.FileReader;
import java.io.Reader;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
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
    private HashMap<Vector3D, Vector3D> discarted;
    private String name;

    public Model(String name) throws Exception {
        this.views = new ArrayList<>();
        this.vertices = new HashSet<>();
        this.discarted = new HashMap<>();
        this.edges = new ArrayList<>();
        this.name = name;

        // A model consists of subdirectories. Each subdirectory stores the
        // information of a different view. Each view consists of the files
        // camera.json and plane.bmp.

        for (File file : (new File("models/" + name)).listFiles()) {
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
        final View view1 = this.views.get(0);
        final View view2 = this.views.get(1);

        for (final Vector3D v1 : view1.vertices) {
            final Line line1 = new Line(v1, v1.add(view1.vy), 0.0001);
            boolean intersected = false;

            for (final Vector3D v2 : view2.vertices) {
                // Check if the line which has direction 'view0.vy' and passes
                // through 'p1' intersects with the line which has direction 
                // 'view1.vy' and passes through 'p2'.

                final Line line2 = new Line(v2, v2.add(view2.vy), 0.0001);
                final Vector3D intersection = line1.intersection(line2);

                if (intersection != null) {
                    this.vertices.add(intersection);
                    intersected = true;
                }
            }

            if (!intersected) {
                this.discarted.put(v1, view1.vy);
            }
        }
    }

    public void refineModelVertices() {
        // TODO Use a iterator to skip the fist two elements so there is no need
        // to get each view using indexing.

        for (int i = 2; i < this.views.size(); ++i) {
            // Given a new view, back project all the current model vertices
            // into the view image plane and eliminate those model vertices 
            // which its back projection is not part of the contour or interior
            // of the countour of the object.

            final Iterator<Vector3D> vertex_iterator = this.vertices.iterator();
            final View view = this.views.get(i);

            while (vertex_iterator.hasNext()) {
                Vector2D projection = view.realToPlanePoint(vertex_iterator.next());
                projection = view.planeToImageCoord(projection);
                final int x = (int) projection.getX();
                final int z = (int) projection.getY();
                final int pixel_value = view.plane.getRGB(x, z) & 0xff; 

                if(pixel_value == ImageProcessing.PIXEL_BACKGROUND) {
                    vertex_iterator.remove();
                }
            }

            /*final Iterator<Pair<Vector3D, Vector3D>> it = discarted_vertices.iterator();

            while (it.hasNext()) {
                final Pair<Vector3D, Vector3D> discarted_pair = it.next();
                final Vector3D discarted_vertex = discarted_pair.getKey();
                final Vector3D discarted_vy = discarted_pair.getValue();
                Line discarted_line = new Line(discarted_vertex, 
                    discarted_vertex.add(discarted_vy), 0.0001);

                for (Vector3D vertex : view.vertices) {
                    Line view_line = new Line(vertex, vertex.add(view.vy), 0.0001);
                    Vector3D intersection = discarted_line.intersection(view_line);
                    
                    if (intersection != null) {
                        this.vertices.add(intersection);
                        it.remove();
                        break;
                    }
                }
            }*/
        }
    }

    public void generateEdges() {

        // TODO edges over the object surface.
        // We will try to generate a edge in each axis direction (X,Y,Z) for each
        // vertex in the model. Edges are formed between two vertices in a same axis
        // direction (and line) that have the minimum distance between each other.
        // This cant work with models with gaps.

        for (final Vector3D vertex : this.vertices) {
            Vector3D min_x = new Vector3D(Double.MAX_VALUE, 0, 0);
            Vector3D min_y = new Vector3D(0, Double.MAX_VALUE, 0);
            Vector3D min_z = new Vector3D(0, 0, Double.MAX_VALUE);

            final double x = vertex.getX();
            final double y = vertex.getY();
            final double z = vertex.getZ();

            for (final Vector3D other : this.vertices) {
                final double ox = other.getX();
                final double oy = other.getY();
                final double oz = other.getZ();

                // Check for horizontal (width) edges (along the X axis)
                if ((ox > x) && (oy == y) && (oz == z) && (ox < min_x.getX())) {
                    min_x = other;
                }

                // Check for horizontal (depth) edges (along the Y axis)
                if ((oy > y) && (ox == x) && (oz == z) && (oy < min_y.getY())) {
                    min_y = other;
                }

                // Check for vertical edges (along the Z axis)
                if ((oz > z) && (ox == x) && (oy == y) && (oz < min_z.getZ())) {
                    min_z = other;
                }
            }

            if (min_x.getX() != Double.MAX_VALUE) { 
                this.edges.add(new Pair<>(vertex, min_x));
            }

            if (min_y.getY() != Double.MAX_VALUE) { 
                this.edges.add(new Pair<>(vertex, min_y));
            }

            if (min_z.getZ() != Double.MAX_VALUE) { 
                this.edges.add(new Pair<>(vertex, min_z));
            }
        }
    }
   
    @Override
    public String toString() {
        String out = "[Model '" + this.name + "']\n";
        for (View view : this.views) { out += view + "\n"; }
        return out;
    }
}