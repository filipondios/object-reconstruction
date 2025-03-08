package com.reconstruction;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import java.util.List;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
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
import org.apache.commons.math3.util.Pair;
import org.apache.commons.math3.geometry.euclidean.threed.Line;
import org.apache.commons.math3.geometry.euclidean.threed.Plane;


public class Model {
    
    // Constants about Models data storage
    private static final String MODEL_DIR   = "models/";
    private static final String PLANE_FILE  = "/plane.bmp";
    private static final String CAMERA_FILE = "/camera.yaml";

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
            // Load the camera position and orientation vectors
            final ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
            final View view = mapper.readValue(new File(view_path + CAMERA_FILE), View.class);
            
            // Load the view projection plane
            final BufferedImage view_image = ImageIO.read(new File(view_path + PLANE_FILE));
            view.extractVerticesFromImage(view_image);
            this.views.add(view);
        }

        // Sort the list of views from the highest to the lowest number 
        // of vertices so there are more chances to get a successful 
        // reconstruction earlier.
        Collections.sort(this.views, new Comparator<View>() {
            @Override
            public int compare(View v1, View v2) {
                final int v1_vertices = v1.getVertices().size();
                final int v2_vertices = v2.getVertices().size();
                return Integer.compare(v2_vertices, v1_vertices);
            }
        });
    }


    public void initialReconstruction() {
        final View view1 = this.views.get(0);
        final View view2 = this.views.get(1);

        for (final Vector3D p1 : view1.getVertices()) {
            for (final Vector3D p2 : view2.getVertices()) {
                // Check if the line which has direction 'view0.vy' and passes
                // through 'p1' intersects with the line which has direction 
                // 'view1.vy' and passes through 'p2'.

                final Line line1 = new Line(p1, p1.add(view1.getVy()), 0.0001);
                final Line line2 = new Line(p2, p2.add(view2.getVy()), 0.0001);
                final Vector3D intersection = line1.intersection(line2);

                if (line1.intersection(line2) != null) {
                    this.vertices.add(intersection);
                }
            }
        }
    }

    public void refineModel() {
        for (int i = 2; i < this.views.size(); ++i) {
            // Given a new view, back project all the current model vertices
            // into the view image plane and eliminate those model vertices 
            // which its back projection is not found in the image plane.
            final View current = this.views.get(i);
            final Plane view_plane = new Plane(current.getVertices().get(0),
                current.getVy(), 0.001);

            Iterator<Vector3D> iterator = this.vertices.iterator();
            while (iterator.hasNext()) {
                Vector3D vertex = iterator.next();
                final Line line = new Line(vertex, vertex.add(current.getVy()), 0.0001);
                final Vector3D intersection = view_plane.intersection(line);
                
                if(!current.getVertices().contains(intersection)) {
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