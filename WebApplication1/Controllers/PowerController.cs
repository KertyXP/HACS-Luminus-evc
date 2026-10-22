using Microsoft.AspNetCore.Mvc;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Power;
using System.Collections.Specialized;

namespace WebApplication1.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class PowerController : ControllerBase
    {

        public PowerController()
        {
        }

        [HttpGet(Name = "GetPower")]
        public LuminusData Get()
        {
            var o = GetLuminusData();
            return o;
        }


        private LuminusData GetLuminusData()
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
                var json = JArray.Parse(t).Last().ToString().Replace(".", "");
                var luminusTotalConsumption = JsonConvert.DeserializeObject<LuminusTotalConsumption>(json);


                LuminusData? data = null;
                try
                {
                    var t2 = client.DownloadString("https://luminus.evc-net.com/api/ajax?requests=%7B%220%22%3A%7B%22handler%22%3A%22%5C%5CLMS%5C%5CEV%5C%5CAsyncServices%5C%5CRechargeSpotsAsyncService%22%2C%22method%22%3A%22overview%22%2C%22params%22%3A%7B%22rechargeSpotId%22%3A%221234606393%22%7D%7D%7D");
                    data = JsonConvert.DeserializeObject<LuminusData>(JArray.Parse(t2).First().First().ToString());
                }
                catch
                {
                    data = new LuminusData()
                    {
                        Cardid = string.Empty,
                        CardsIdx = string.Empty,
                        CustomersIdx = string.Empty,
                        CustomerName = string.Empty,
                        Connector = string.Empty,
                        Channel = 0,
                        CardTypeIcon = string.Empty,
                        EventData = string.Empty,
                        Icon = string.Empty,
                        IsGlobalCard = string.Empty,
                        IsSelf = true,
                        MomPowerKw = 0,
                        Notification = string.Empty,
                        Soc = null,
                        Status = 0,
                        TransactionTimeHM = string.Empty,
                        TransEnergyDeliveredKwh = 0
                    };
                }
                

                data.pastConsumptionNumber = luminusTotalConsumption.Number;
                data.pastConsumptionUnit = luminusTotalConsumption.Unit;

                return data;
            }
        }




    }

    public partial class LuminusData
    {
        [JsonProperty("CHANNEL")]
        public long Channel { get; set; }

        [JsonProperty("CONNECTOR")]
            public string Connector { get; set; }

        [JsonProperty("MOM_POWER_KW")]
        public double MomPowerKw { get; set; }

        [JsonProperty("SOC")]
        public object Soc { get; set; }

        [JsonProperty("TRANS_ENERGY_DELIVERED_KWH")]
        public double TransEnergyDeliveredKwh { get; set; }

        [JsonProperty("TRANSACTION_TIME_H_M")]
        public string TransactionTimeHM { get; set; }

        [JsonProperty("EVENT_DATA")]
        public string EventData { get; set; }

        [JsonProperty("CARDID")]
        public string Cardid { get; set; }

        [JsonProperty("CARD_TYPE_ICON")]
        public string CardTypeIcon { get; set; }

        [JsonProperty("CARDS_IDX")]
        public string CardsIdx { get; set; }

        [JsonProperty("CUSTOMERS_IDX")]
        public object CustomersIdx { get; set; }

        [JsonProperty("CUSTOMER_NAME")]
        public string CustomerName { get; set; }

        [JsonProperty("IS_SELF")]
        public bool IsSelf { get; set; }

        [JsonProperty("IS_GLOBAL_CARD")]
        public string IsGlobalCard { get; set; }

        [JsonProperty("STATUS")]
        public long Status { get; set; }

        [JsonProperty("NOTIFICATION")]
        public string Notification { get; set; }

        [JsonProperty("ICON")]
        public string Icon { get; set; }
        public double pastConsumptionNumber { get; set; }
        public string pastConsumptionUnit { get; set; }
        public double totalConsumptionNumber => pastConsumptionNumber + TransEnergyDeliveredKwh;

    }


    public partial class LuminusTotalConsumption
    {
        public long Number { get; set; }
        public string Unit { get; set; }
    }
}
