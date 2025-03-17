package com.app;

import java.io.IOException;
import com.reconstruction.Model;

public class Main {

    public static void main(String args[]) throws IOException {
        // Try to load the 3D Model
        Model model = new Model("cross");
        model.initialReconstruction();
        model.refineModel();
        model.generateEdges();
        System.out.println(model);

        // Render the obtained 3D model
        ModelRender render = new ModelRender(model);
        render.initialize();
        render.renderLoop();
    }
}