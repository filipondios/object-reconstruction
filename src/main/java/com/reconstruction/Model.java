package com.reconstruction;

import com.raylib.Raylib.Vector3;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import javax.imageio.ImageIO;
import org.yaml.snakeyaml.Yaml;


public class Model {

    private ArrayList<View> views;
    private ArrayList<Vector3> vertices;
    private String name;
    private int nextView;
    
    // Class unique instance
    private static Model model;

    @SuppressWarnings({ "unchecked", "resource" })
    private Model(String name) throws IOException {
        
        this.views = new ArrayList<>();
        this.vertices = new ArrayList<>();
        this.name = name;
        this.nextView = 0;

        // Try to load the model views from its directory.
        Set<Path> views = Files.list(Paths.get("models/model_" + name))
            .filter(Files::isDirectory)
            .collect(Collectors.toSet());

        for (Path view_path : views) {
            String path = view_path.toString();
            BufferedImage view_image = ImageIO.read(new File(path + "/plane.bmp"));
            
            // Load the camera position and orientation vectors
            InputStream stream = new FileInputStream(new File(path + "/camera.yml"));
            Yaml yaml = new Yaml();
            Map<String, Object> data = yaml.load(stream);
            Map<String, Integer> v;

            v = (Map<String, Integer>) data.get("position");
            Vector3 position = new Vector3()
                .x((float) v.get("x"))
                .y((float) v.get("y"))
                .z((float) v.get("z"));

            v = (Map<String, Integer>) data.get("vx");
            Vector3 vx = new Vector3()
                .x((float) v.get("x"))
                .y((float) v.get("y"))
                .z((float) v.get("z"));

            v = (Map<String, Integer>) data.get("vy");
            Vector3 vy = new Vector3()
                .x((float) v.get("x"))
                .y((float) v.get("y"))
                .z((float) v.get("z"));
            
            v = (Map<String, Integer>) data.get("vz");
            Vector3 vz = new Vector3()
                .x((float) v.get("x"))
                .y((float) v.get("y"))
                .z((float) v.get("z"));
            
            this.views.add(new View(
                (String) data.get("name"),
                view_image, 
                position,
                vx, vy, vz
            ));
        }   
    }
    
    public static Model loadModel(String name) throws IOException {
        if (model == null) { model = new Model(name); } 
        return model;
    }

    public ArrayList<View> getViews() { 
        return this.views;
    }
    
    public ArrayList<Vector3> getVertices() { 
        return this.vertices;
    }

    @Override
    public String toString() {
        String out = "[Model '" + this.name + "']\n";
        for (View view : this.views) { out += view + "\n"; }
        return out;
    }
}