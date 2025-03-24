package com.app;

import com.core.Model;
import com.core.ModelRender;

public class Main {

    public static void main(String args[]) throws Exception {
        // Try to load the 3D Model
        Model model = new Model("jar");
        model.generateInitialReconstruction();
        model.refineModelVertices();
        model.generateEdges();
        System.out.println(model);

        // Render the obtained 3D model
        ModelRender render = new ModelRender(model);
        render.showModelVertices(false);
        render.showViewVertices(false);
        render.initialize();
        render.renderLoop();
    }
}