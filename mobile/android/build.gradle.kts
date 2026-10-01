allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

val newBuildDir: Directory =
    rootProject.layout.buildDirectory
        .dir("../../build")
        .get()
rootProject.layout.buildDirectory.value(newBuildDir)

subprojects {
    val newSubprojectBuildDir: Directory = newBuildDir.dir(project.name)
    project.layout.buildDirectory.value(newSubprojectBuildDir)
}
subprojects {
    project.evaluationDependsOn(":app")
    tasks.matching { it.name.contains("Kotlin") }.configureEach {
        try {
            val task = this
            val method = task.javaClass.getMethod("getKotlinOptions")
            val options = method.invoke(task)
            val getArgs = options.javaClass.getMethod("getFreeCompilerArgs")
            @Suppress("UNCHECKED_CAST")
            val args = getArgs.invoke(options) as? MutableList<String>
            args?.add("-Xskip-metadata-version-check")
        } catch (_: Exception) {}
    }
}

tasks.register<Delete>("clean") {
    delete(rootProject.layout.buildDirectory)
}
