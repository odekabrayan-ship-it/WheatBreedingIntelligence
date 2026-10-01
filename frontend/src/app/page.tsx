"use client";

import { FormEvent, useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

interface Project {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
}

const navigation = [
  "Dashboard",
  "Projects",
  "Data",
  "Analyses",
  "Models",
  "Predictions",
  "Candidates",
  "Reports",
];

const metrics = [
  {
    label: "Active projects",
    description: "Breeding projects currently being developed",
  },
  {
    label: "Datasets",
    value: "0",
    description: "Genomic, phenotypic, and environmental datasets",
  },
  {
    label: "Analyses",
    value: "0",
    description: "Completed or running scientific analyses",
  },
  {
    label: "Models",
    value: "0",
    description: "Validated prediction models",
  },
];

export default function Home() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [projects, setProjects] = useState<Project[]>([]);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [projectsError, setProjectsError] = useState("");
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [creatingProject, setCreatingProject] = useState(false);
  const [createError, setCreateError] = useState("");

  const loadProjects = async () => {
    setProjectsLoading(true);
    setProjectsError("");

    try {
      const response = await fetch(`${API_URL}/projects/`);

      if (!response.ok) {
        throw new Error("Failed to load projects");
      }

      const data: Project[] = await response.json();
      setProjects(data);
    } catch {
      setProjectsError("Unable to load projects from the API.");
    } finally {
      setProjectsLoading(false);
    }
  };

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend request failed");
        }
        return response.json();
      })
      .then((data) => {
        setBackendStatus(
          data.status === "healthy" ? "Connected" : "Unavailable"
        );
      })
      .catch(() => {
        setBackendStatus("Unavailable");
      });

    loadProjects();
  }, []);

  const handleCreateProject = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!projectName.trim()) {
      setCreateError("Project name is required.");
      return;
    }

    setCreatingProject(true);
    setCreateError("");

    try {
      const response = await fetch(`${API_URL}/projects/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: projectName.trim(),
          description: projectDescription.trim() || null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to create project");
      }

      const newProject: Project = await response.json();

      setProjects((currentProjects) => [newProject, ...currentProjects]);
      setProjectName("");
      setProjectDescription("");
      setShowCreateProject(false);
    } catch {
      setCreateError("Unable to create the project. Please try again.");
    } finally {
      setCreatingProject(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 shrink-0 border-r border-slate-200 bg-white lg:flex lg:flex-col">
          <div className="border-b border-slate-200 px-6 py-5">
            <div className="text-lg font-semibold tracking-tight">
              WheatBI
            </div>
            <p className="mt-1 text-xs text-slate-500">
              WheatBreeding Intelligence
            </p>
          </div>

          <nav className="flex-1 px-3 py-5">
            <p className="px-3 pb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
              Workspace
            </p>

            <div className="space-y-1">
              {navigation.map((item, index) => (
                <button
                  key={item}
                  className={`w-full rounded-lg px-3 py-2.5 text-left text-sm transition ${
                    index === 0
                      ? "bg-slate-100 font-medium text-slate-900"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                >
                  {item}
                </button>
              ))}
            </div>
          </nav>

          <div className="border-t border-slate-200 p-4">
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs font-medium text-slate-700">
                Scientific decision support
              </p>
              <p className="mt-1 text-xs leading-5 text-slate-500">
                Built for reproducible breeding research and evidence-based
                decisions.
              </p>
            </div>
          </div>
        </aside>

        <main className="min-w-0 flex-1">
          <header className="border-b border-slate-200 bg-white">
            <div className="flex min-h-16 items-center justify-between px-5 sm:px-8">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  WheatBreeding Intelligence
                </p>
                <h1 className="text-xl font-semibold tracking-tight">
                  Dashboard
                </h1>
              </div>

              <div className="flex items-center gap-4">
                <div className="hidden items-center gap-2 sm:flex">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${
                      backendStatus === "Connected"
                        ? "bg-emerald-500"
                        : "bg-amber-500"
                    }`}
                  />
                  <span className="text-xs font-medium text-slate-600">
                    API: {backendStatus}
                  </span>
                </div>

                <div className="hidden text-right md:block">
                  <p className="text-sm font-medium text-slate-700">
                    Research workspace
                  </p>
                  <p className="text-xs text-slate-500">Local development</p>
                </div>

                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900 text-sm font-medium text-white">
                  W
                </div>
              </div>
            </div>
          </header>

          <div className="mx-auto max-w-7xl px-5 py-8 sm:px-8">
            <section>
              <div className="max-w-3xl">
                <p className="text-sm font-medium text-slate-500">
                  Breeding intelligence workspace
                </p>

                <h2 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">
                  Turn breeding data into actionable scientific insight.
                </h2>

                <p className="mt-3 max-w-2xl text-base leading-7 text-slate-600">
                  Integrate genomic, phenotypic, environmental, and
                  experimental data to support prediction, explainability,
                  uncertainty analysis, and breeding decisions.
                </p>
              </div>

              <div className="mt-6">
                <button
                  onClick={() => {
                    setCreateError("");
                    setShowCreateProject(true);
                  }}
                  className="rounded-lg bg-slate-900 px-5 py-3 text-sm font-medium text-white transition hover:bg-slate-700"
                >
                  Create project
                </button>
              </div>
            </section>

            {showCreateProject && (
              <section className="mt-6 rounded-xl border border-slate-200 bg-white p-6">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      Create a research project
                    </h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Define the project before adding breeding data and
                      analyses.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => setShowCreateProject(false)}
                    className="text-sm text-slate-500 hover:text-slate-900"
                  >
                    Cancel
                  </button>
                </div>

                <form
                  onSubmit={handleCreateProject}
                  className="mt-6 grid gap-5"
                >
                  <div>
                    <label
                      htmlFor="project-name"
                      className="text-sm font-medium text-slate-700"
                    >
                      Project name
                    </label>
                    <input
                      id="project-name"
                      value={projectName}
                      onChange={(event) => setProjectName(event.target.value)}
                      placeholder="e.g. Wheat Climate Resilience Study"
                      maxLength={200}
                      className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="project-description"
                      className="text-sm font-medium text-slate-700"
                    >
                      Description
                    </label>
                    <textarea
                      id="project-description"
                      value={projectDescription}
                      onChange={(event) =>
                        setProjectDescription(event.target.value)
                      }
                      placeholder="Briefly describe the scientific purpose of this project."
                      rows={4}
                      className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
                    />
                  </div>

                  {createError && (
                    <p className="text-sm text-red-600">{createError}</p>
                  )}

                  <div>
                    <button
                      type="submit"
                      disabled={creatingProject}
                      className="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      {creatingProject ? "Creating..." : "Create project"}
                    </button>
                  </div>
                </form>
              </section>
            )}

            <section className="mt-10 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {metrics.map((metric) => (
                <div
                  key={metric.label}
                  className="rounded-xl border border-slate-200 bg-white p-5"
                >
                  <p className="text-sm font-medium text-slate-500">
                    {metric.label}
                  </p>
                  <p className="mt-3 text-3xl font-semibold tracking-tight">
                    {metric.label === "Active projects"
                      ? projectsLoading
                        ? "..."
                        : projects.length
                      : metric.value}
                  </p>
                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    {metric.description}
                  </p>
                </div>
              ))}
            </section>

            <section className="mt-8 grid gap-6 lg:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-white p-6 lg:col-span-2">
                <div>
                  <h3 className="font-semibold text-slate-900">
                    Research projects
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    Projects currently stored in the WheatBI research
                    workspace
                  </p>
                </div>

                <div className="mt-6">
                  {projectsLoading && (
                    <p className="text-sm text-slate-500">
                      Loading projects...
                    </p>
                  )}

                  {projectsError && (
                    <p className="text-sm text-red-600">{projectsError}</p>
                  )}

                  {!projectsLoading &&
                    !projectsError &&
                    projects.length === 0 && (
                      <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
                        <p className="text-sm font-medium text-slate-700">
                          No projects yet
                        </p>
                        <p className="mt-1 text-xs text-slate-500">
                          Create your first WheatBI research project to begin.
                        </p>
                      </div>
                    )}

                  {!projectsLoading &&
                    !projectsError &&
                    projects.length > 0 && (
                      <div className="space-y-3">
                        {projects.map((project) => (
                          <div
                            key={project.id}
                            className="rounded-lg border border-slate-200 p-4"
                          >
                            <div className="flex items-start justify-between gap-4">
                              <div>
                                <h4 className="font-medium text-slate-900">
                                  {project.name}
                                </h4>
                                {project.description && (
                                  <p className="mt-1 text-sm leading-6 text-slate-500">
                                    {project.description}
                                  </p>
                                )}
                              </div>

                              <span className="shrink-0 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700">
                                Active
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white p-6">
                <h3 className="font-semibold text-slate-900">
                  Scientific principles
                </h3>

                <ul className="mt-5 space-y-4 text-sm">
                  {[
                    "Data quality before modeling",
                    "Breeding-relevant validation",
                    "Explainable predictions",
                    "Uncertainty-aware decisions",
                    "Reproducible research",
                    "Human decision support",
                  ].map((principle) => (
                    <li key={principle} className="flex gap-3">
                      <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
                      <span className="text-slate-600">{principle}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            <section className="mt-8 grid gap-6 lg:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-white p-6 lg:col-span-2">
                <div>
                  <h3 className="font-semibold text-slate-900">
                    Research workflow
                  </h3>
                  <p className="mt-1 text-sm text-slate-500">
                    The core WheatBI analytical pathway
                  </p>
                </div>

                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  {[
                    ["01", "Create project", "Define the breeding objective"],
                    [
                      "02",
                      "Upload data",
                      "Bring genomic and phenotypic data together",
                    ],
                    [
                      "03",
                      "Quality control",
                      "Check structure, completeness, and validity",
                    ],
                    [
                      "04",
                      "Analyze",
                      "Run statistical and machine-learning workflows",
                    ],
                    [
                      "05",
                      "Validate",
                      "Evaluate models using breeding-relevant validation",
                    ],
                    [
                      "06",
                      "Interpret",
                      "Explore explanations and uncertainty",
                    ],
                  ].map(([number, title, description]) => (
                    <div
                      key={number}
                      className="rounded-lg border border-slate-100 bg-slate-50 p-4"
                    >
                      <span className="text-xs font-semibold text-slate-400">
                        {number}
                      </span>
                      <h4 className="mt-2 text-sm font-semibold text-slate-800">
                        {title}
                      </h4>
                      <p className="mt-1 text-xs leading-5 text-slate-500">
                        {description}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}
