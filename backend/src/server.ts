import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import dotenv from "dotenv";
import cron from "node-cron";
import apiRoutes from "./routes";
import { notFoundHandler, errorHandler } from "./middleware/errorMiddleware";
import { regeneratePatterns } from "./services/patternService";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors({ origin: process.env.CORS_ORIGIN || 'http://localhost:5173' }));
app.use(express.json());

// MongoDB Connection
const MONGO_URI = process.env.MONGO_URI;

if (!MONGO_URI) {
  console.error("❌ MONGO_URI is not defined in .env");
  process.exit(1);
}

// Test Route
app.get("/", (_req, res) => {
  res.json({
    message: "Backend API is running 🚀",
  });
});

// Health Check
app.get("/api/health", (_req, res) => {
  res.json({
    status: "OK",
    database:
      mongoose.connection.readyState === 1 ? "Connected" : "Disconnected",
  });
});

// All feature routes (auth, reports, dashboard, patterns, interventions, audit-logs)
app.use("/api", apiRoutes);

// 404 + centralized error handler must be registered LAST, after all routes.
app.use(notFoundHandler);
app.use(errorHandler);

mongoose
  .connect(MONGO_URI)
  .then(() => {
    console.log("✅ MongoDB connected");

    app.listen(PORT, () => {
      console.log(`🚀 Server running on http://localhost:${PORT}`);
    });

    // Nightly at 02:00 server time: recompute SIF precursor patterns from
    // whatever reports/analyses have accumulated during the day. This is in
    // addition to the on-demand regeneration that runs after every
    // POST /reports/:id/analyze (see reportsController.analyzeReport).
    cron.schedule("0 2 * * *", async () => {
      try {
        const updated = await regeneratePatterns();
        console.log(`🔁 [cron] Pattern regeneration complete: ${updated} pattern(s) updated`);
      } catch (err) {
        console.error("[cron] Pattern regeneration failed:", err);
      }
    });
  })
  .catch((error) => {
    console.error("❌ MongoDB connection failed:", error);
    process.exit(1);
  });

process.on("unhandledRejection", (reason) => {
  console.error("Unhandled promise rejection:", reason);
});
