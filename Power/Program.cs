using Newtonsoft.Json;
using Power;
using System.Collections.Specialized;
using System.Text.Json;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateSlimBuilder(args);

builder.Services.ConfigureHttpJsonOptions(options =>
{
});

var app = builder.Build();

var sampleTodos = new Todo[] {
    new(1, "Walk the dog"),
    new(2, "Do the dishes", DateOnly.FromDateTime(DateTime.Now)),
    new(3, "Do the laundry", DateOnly.FromDateTime(DateTime.Now.AddDays(1))),
    new(4, "Clean the bathroom"),
    new(5, "Clean the car", DateOnly.FromDateTime(DateTime.Now.AddDays(2)))
};

var todosApi = app.MapGroup("/todos");
todosApi.MapGet("/", () => GetLuminusKwh);
todosApi.MapGet("/{id}", (int id) =>
    sampleTodos.FirstOrDefault(a => a.Id == id) is { } todo
        ? Results.Ok(todo)
        : Results.NotFound());

app.Run();

string GetLuminusKwh()
{
    using (var client = new CookieWebClient())
    {

        var loginData = new NameValueCollection
        {
            { "emailField", "simon.marchal" },
            { "passwordField", "SimonMarchal1$" },
            { "Login", "S'identifier" }
        };

        // Login into the website (at this point the Cookie Container will do the rest of the job for us, and save the cookie for the next calls)
        client.UploadValues("https://luminus.evc-net.com/RechargeSpots/Detail/1234606393", "POST", loginData);

        // Call authenticated resources
        var t = client.DownloadString("https://luminus.evc-net.com/api/ajax?requests=%7B%220%22%3A%7B%22handler%22%3A%22%5C%5CLMS%5C%5CEV%5C%5CAsyncServices%5C%5CDashboardAsyncService%22%2C%22method%22%3A%22occupancy%22%2C%22params%22%3A%7B%22mode%22%3A7%2C%22rechargeSpotIds%22%3A%5B%221234606393%22%5D%2C%22maxCache%22%3A600%7D%7D%2C%221%22%3A%7B%22handler%22%3A%22%5C%5CLMS%5C%5CEV%5C%5CAsyncServices%5C%5CDashboardAsyncService%22%2C%22method%22%3A%22current%22%2C%22params%22%3A%7B%22mode%22%3A1%2C%22rechargeSpotIds%22%3A%5B%221234606393%22%5D%7D%7D%2C%222%22%3A%7B%22handler%22%3A%22%5C%5CLMS%5C%5CEV%5C%5CAsyncServices%5C%5CDashboardAsyncService%22%2C%22method%22%3A%22totalUsage%22%2C%22params%22%3A%7B%22mode%22%3A%22rechargeSpot%22%2C%22rechargeSpotIds%22%3A%5B%221234606393%22%5D%2C%22maxCache%22%3A3600%7D%7D%7D");
        // deserialize t to Luminus object
        var luminus = JsonConvert.DeserializeObject<LuminusElement>(t);

        return "toto";
    }
}

public record Todo(int Id, string? Title, DateOnly? DueBy = null, bool IsComplete = false);


