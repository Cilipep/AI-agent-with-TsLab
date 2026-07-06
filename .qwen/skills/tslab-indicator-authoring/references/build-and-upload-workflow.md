# Build and Upload Workflow (Two Modes)

This reference is **self-contained** and designed to be usable in a delivery build.

Goal: turn a C# handler class into a loaded indicator DLL in TSLab, with human description.

## Mode A: Agent Can Build Locally (SDK Available)

Use when the agent environment has:
- `dotnet` SDK
- Access to TSLab reference assemblies needed for compilation (at least `TSLab.Script.dll` + its deps like `TSLab.DataSource.dll`)

### Steps

1. Create a small class library project (one-time or per indicator set)
   - Target the same runtime as the host (commonly `net9.0` for this repo; match your deployment).
2. Add references to TSLab assemblies
   - Prefer package references if you have them.
   - Otherwise reference local DLLs from the TSLab installation/build output.
   - Minimum: reference `TSLab.Script.dll` (handler contracts + helper APIs like `Series` / `Indicators`).
   - Common additional refs for custom indicators:
     - `TSLab.DataSource.dll` (cache delegates, memory management interfaces used by `IContext`)
     - `TSLab.Utility.dll` (utility extensions like `AsReadOnly()` adapters used with `Series.*`)
3. Add the handler `.cs` file(s)
4. (Optional) Add resources for display name/description
   - Add a `.resx` and include keys:
     - `<TypeName>.Name`
     - `<TypeName>.Description`
5. Build
   - Debug build for breakpoints: generates `.pdb`
   - Release build for deployment
6. Load into TSLab
   - Disk hot reload: copy `.dll` + `.pdb` into HandlersFolder
   - Or DB upload via API (recommended for remote/distributed use):
     - `POST /api/indicator-dlls/{name}` with multipart `file` and optional `description`
7. Verify
   - `GET /api/handlers` should list the new `typeName`
   - `GET /api/handlers/{typeName}` should show IO/params

### Minimal `.csproj` sketch (adapt references)

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net9.0</TargetFramework>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
  </PropertyGroup>

  <ItemGroup>
    <!-- Point these to the TSLab runtime/build output you are targeting -->
    <Reference Include="TSLab.Script">
      <HintPath>PATH_TO_TSLab.Script.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="TSLab.DataSource">
      <HintPath>PATH_TO_TSLab.DataSource.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="TSLab.Utility">
      <HintPath>PATH_TO_TSLab.Utility.dll</HintPath>
      <Private>false</Private>
    </Reference>
  </ItemGroup>
</Project>
```

### Minimal command sketch (adapt paths)

```powershell
# Create project
dotnet new classlib -n MyIndicators -o MyIndicators

# Add your handler files under MyIndicators\
# Ensure references to TSLab.* assemblies are resolvable (PackageReference or <Reference HintPath=...>)

# Build Debug (PDB for debugging)
dotnet build .\\MyIndicators\\MyIndicators.csproj -c Debug

# DLL output (example):
# .\\MyIndicators\\bin\\Debug\\net9.0\\MyIndicators.dll
```

## Mode B: Agent Cannot Build (No SDK / No References)

Use when the agent environment cannot compile (common for production "AI agent" deployments).

### Steps

1. Generate sources only
   - Produce:
     - `MyIndicators.csproj`
     - handler `.cs` files
     - optional `.resx` resources
2. Provide a CI/dev build recipe
   - The build machine must have:
     - `dotnet` SDK
     - access to TSLab reference assemblies
3. After a build produces `*.dll` (+ optional `*.pdb`), upload to TSLab
   - DB upload: `POST /api/indicator-dlls/{name}`
   - Provide `description` in the request so it is returned by the API
4. Verify via `/api/handlers`

### What the agent should report

- Which mode was used (A build+upload, or B source-only)
- Build commands (if mode B: commands for CI/dev)
- Upload method (disk vs DB API) and `name`
- Resulting handler `typeName`

## Upload details: description vs embedded resources

- API `description` (multipart form field) is stored with the DB record and returned by `GET /api/indicator-dlls`.
- Handler block display name/description should come from embedded resources when present:
  - `<TypeName>.Name`
  - `<TypeName>.Description`

Treat `/api/handlers/{typeName}` as the runtime contract source of truth.
