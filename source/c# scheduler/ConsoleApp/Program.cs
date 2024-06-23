using System;
using System.IO;
using System.Text.Json;
using Microsoft.Win32.TaskScheduler;
public class AppConfig
{
    public int CheckIntervalMinutes { get; set; }
}
class Program
{
    static void Main(string[] args)
    {
        // Get the current working directory
        string currentDirectory = Directory.GetCurrentDirectory();
        Console.WriteLine(currentDirectory);
        string jsonFilePath = Path.Combine(currentDirectory, "ConfigSchedule.json");
        try
        {
            // Read the entire JSON file into a string
            string jsonString = File.ReadAllText(jsonFilePath);

            // Deserialize the JSON string into AppConfig object
            AppConfig config = JsonSerializer.Deserialize<AppConfig>(jsonString);

            if (config != null)
            {
                int intervalMinutes = config.CheckIntervalMinutes;

                string taskName = "Cold Turkey Scheduler";

                // Combine the current directory with the relative path to get the full executable path
                string executablePath = Path.Combine(currentDirectory, "auto_enabler.exe");

                using (TaskService taskService = new TaskService())
                {
                    TaskDefinition taskDefinition = taskService.NewTask();

                    taskDefinition.RegistrationInfo.Description = "Run Cold Turkey Checker every specified interval";

                    taskDefinition.Actions.Add(new ExecAction(executablePath));

                    // Configure a trigger to run at the specified interval
                    taskDefinition.Triggers.Add(new TimeTrigger
                    {
                        StartBoundary = DateTime.Now,
                        Repetition = new RepetitionPattern(TimeSpan.FromMinutes(intervalMinutes), TimeSpan.FromDays(9131))
                    });

                    // Task settings to run regardless of power status
                    taskDefinition.Settings.StartWhenAvailable = true;
                    taskDefinition.Settings.DisallowStartIfOnBatteries = false;
                    taskDefinition.Settings.StopIfGoingOnBatteries = false;
                    taskDefinition.Settings.ExecutionTimeLimit = TimeSpan.FromDays(3);
                    taskDefinition.Settings.MultipleInstances = TaskInstancesPolicy.IgnoreNew;

                    taskService.RootFolder.RegisterTaskDefinition(taskName, taskDefinition);

                    Console.WriteLine($"Cold Turkey Updater scheduled/updated successfully to run every {intervalMinutes} minutes.");
                }
            }
            else
            {
                Console.WriteLine("Failed to deserialize JSON or AppConfig is null.");
            }
        }
        catch (FileNotFoundException)
        {
            Console.WriteLine("File not found.");
        }
        catch (JsonException)
        {
            Console.WriteLine("Invalid JSON format.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"An error occurred: {ex.Message}");
        }
        Console.WriteLine("Press ENTER to Exit.");
        Console.ReadLine();
    }
}
