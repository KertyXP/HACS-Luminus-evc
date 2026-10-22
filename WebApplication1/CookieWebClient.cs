namespace Power
{
    using System;
    using System.Net;
    public class CookieWebClient : WebClient
    {
        public CookieContainer CookieContainer { get; private set; }

        /// <summary>
        /// This will instanciate an internal CookieContainer.
        /// </summary>
        public CookieWebClient()
        {
            this.CookieContainer = new CookieContainer();
        }

        protected override WebRequest GetWebRequest(Uri address)
        {
            var request = base.GetWebRequest(address) as HttpWebRequest;
            if (request == null) return base.GetWebRequest(address);
            request.CookieContainer = CookieContainer;
            return request;
        }
    }
}
