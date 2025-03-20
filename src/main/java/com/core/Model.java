package com.core;

import java.util.List;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.Reader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Iterator;
import java.util.stream.Collectors;
import javax.imageio.ImageIO;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.twod.Vector2D;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.util.Pair;
import com.google.gson.Gson;
import com.image.ImageProcessing;


public class Model {
    
    // Constants about Models data storage
    private static final String MODEL_DIR   = "models/";
    private static final String PLANE_FILE  = "/plane.bmp";
    private static final String CAMERA_FILE = "/camera.json";

    private ArrayList<View> views;
    private ArrayList<Vector3D> vertices;
    private ArrayList<Pair<Vector3D, Vector3D>> edges;
    private String name;

    public Model(String name) throws IOException {
        this.views = new ArrayList<>();
        this.vertices = new ArrayList<>();
        this.edges = new ArrayList<>();
        this.name = name;

        final List<Path> views = Files.list(Paths.get(MODEL_DIR, name))
            .filter(Files::isDirectory)
            .collect(Collectors.toList());

        for (final Path view_path : views) {
            // TODO Throw a exception in case there is no camera or view file.  
            // Load the camera position and orientation vectors
            Reader reader = new FileReader(view_path + CAMERA_FILE);
            View view = (new Gson()).fromJson(reader, View.class);
            reader.close();

            // Load the view projection plane
            view.setViewPlane(ImageIO.read(new File(view_path + PLANE_FILE)));
            this.views.add(view);
        }

        // TODO Throw an error if there are less than 3 views.

        // Sort the list of views from the highest to the lowest number 
        // of vertices so there are more chances to get a successful 
        // reconstruction earlier.
        Collections.sort(this.views, new Comparator<View>() {
            @Override
            public int compare(View v1, View v2) {
                final int v1_vertices = v1.vertices.size();
                final int v2_vertices = v2.vertices.size();
                return Integer.compare(v2_vertices, v1_vertices);
            }
        });
    }

    public void initialReconstruction() {
        final View view1 = this.views.get(0);
        final View view2 = this.views.get(1);

        for (final Vector3D v1 : view1.vertices) {

            for (final Vector3D v2 : view2.vertices) {
                // Check if the line which has direction 'view0.vy' and passes
                // through 'p1' intersects with the line which has direction 
                // 'view1.vy' and passes through 'p2'.

                final Line line1 = new Line(v1, v1.add(view1.vy), 0.0001);
                final Line line2 = new Line(v2, v2.add(view2.vy), 0.0001);
                final Vector3D intersection = line1.intersection(line2);

                if (line1.intersection(line2) != null) {
                    this.vertices.add(intersection);
                }
            }
        }
    }

    public void refineModel() {
        // TODO Use a iterator to skip the fist two elements so there is no need
        // to get each view using indexing.

        for (int i = 2; i < this.views.size(); ++i) {
            // Given a new view, back project all the current model vertices
            // into the view image plane and eliminate those model vertices 
            // which its back projection is not part of the contour of the image

            Iterator<Vector3D> iterator = this.vertices.iterator();
            final View view = this.views.get(i);

            while (iterator.hasNext()) {
                Vector2D projection = view.realToPlanePoint(iterator.next());
                projection = view.planeToImageCoord(projection);
                final int x = (int) projection.getX();
                final int z = (int) projection.getY();
                final int pixel_value = view.plane.getRGB(x, z) & 0xff; 

                if(pixel_value == ImageProcessing.PIXEL_BACKGROUND) {
                    iterator.remove();
                }
            }
        }
    }

    public void generateEdges() {

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

    public ArrayList<Vector3D> getVertices() { return this.vertices; }
    public ArrayList<Pair<Vector3D, Vector3D>> getEdges() { return this.edges; }
    public ArrayList<View> getViews() { return this.views; }
    
    @Override
    public String toString() {
        String out = "[Model '" + this.name + "']\n";
        for (View view : this.views) { out += view + "\n"; }
        return out;
    }
}