package com.core;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import com.google.gson.Gson;
import de.vandermeer.asciitable.AsciiTable;
import de.vandermeer.skb.interfaces.transformers.textformat.TextAlignment;

public class Model {

    ArrayList<View> views;
    String name;

    public Model(final String path) throws IOException {
        this.views = new ArrayList<>();
        this.name = path;
        Gson gson = new Gson();       

        for (File modelFile : (new File(path)).listFiles()) {
            final String fileName = modelFile.getCanonicalPath();

            if (modelFile.isDirectory() && View.isViewDir(fileName)) {
                this.views.add(new View(fileName, gson));
            }
        }
    }

    @Override
    public String toString() {
        String result;
        
        AsciiTable table = new AsciiTable();
        table.addRule();
        table.addRow(this.name);
        table.setTextAlignment(TextAlignment.CENTER);
        result = table.render();

        table = new AsciiTable();
        table.addRule();
        table.addRow("View", "Origin", "Vx", "Vy", "Vz");
        table.addRule();

        for (View camera : this.views) {
            table.addRow(
                camera.camera.name,
                camera.camera.position,
                camera.camera.vx,
                camera.camera.vy,
                camera.camera.vz
            );
        }

        table.addRule();
        return "\n" + result + "\n" + table.render();
    }
}