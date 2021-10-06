pluginManagement {
  repositories {
    gradlePluginPortal()
    maven {
      url = uri("s3://jambos-maven.s3.amazonaws.com")
      authentication {
        create<AwsImAuthentication>("awsIm")
      }
    }
  }
  plugins {
    id("com.jambos.python") version "2.1.5"
  }
}
