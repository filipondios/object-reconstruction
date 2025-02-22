package com.reconstruction;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Set;
import java.util.stream.Collectors;
import javax.imageio.ImageIO;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import org.apache.commons.math3.geometry.euclidean.threed.Line;


public class Model {
    
    // Constants about Models data storage
    private static final String MODEL_DIR   = "models/model_";
    private static final String PLANE_FILE  = "/plane.bmp";
    private static final String CAMERA_FILE = "/camera.yml";

    private ArrayList<View> views;
    private ArrayList<Vector3D> vertices;
    private String name;
    
    // Class unique instance
    private static Model model;
    private static int nextView;
   
    private Model(String name) throws IOException {
        this.views = new ArrayList<>();
        this.vertices = new ArrayList<>();
        this.name = name;

        // Try to load the model views from its directory.
        final Set<Path> views = Files.list(Paths.get(MODEL_DIR + name))
            .filter(Files::isDirectory)
            .collect(Collectors.toSet());

        for (Path view_path : views) {          
            // Load the camera position and orientation vectors
            final ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
            final View view = mapper.readValue(new File(view_path + CAMERA_FILE), View.class);
            
            // Load the view projection plane
            final BufferedImage view_image = ImageIO.read(new File(view_path + PLANE_FILE));
            view.extractVerticesFromImage(view_image);
            this.views.add(view);
        }
    }
    
    public static Model loadModel(String name) throws IOException {
        if (model == null) { model = new Model(name); } 
        return model;
    }

    public void initialReconstruction() {
        final View view1 = this.views.get(0);
        final View view2 = this.views.get(1);
        nextView = 2; /* Views 0 and 1 are now used */

        for (Vector3D p1 : view1.getVertices()) {
            for (Vector3D p2 : view2.getVertices()) {
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

    public ArrayList<Vector3D> getVertices() { return this.vertices; }
    public ArrayList<View> getViews() { return this.views; }
    
    @Override
    public String toString() {
        String out = "[Model '" + this.name + "']\n";
        for (View view : this.views) { out += view + "\n"; }
        return out;
    }
}