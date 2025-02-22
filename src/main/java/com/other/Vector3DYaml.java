package com.other;

import java.io.IOException;
import org.apache.commons.math3.geometry.euclidean.threed.Vector3D;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;

public class Vector3DYaml extends JsonDeserializer<Vector3D> {

    @Override
    public Vector3D deserialize(JsonParser p, DeserializationContext ctxt) throws IOException {
        JsonNode node = p.getCodec().readTree(p);
        double x = node.get("x").asDouble();
        double y = node.get("y").asDouble();
        double z = node.get("z").asDouble();
        return new Vector3D(x, y, z);
    }
}