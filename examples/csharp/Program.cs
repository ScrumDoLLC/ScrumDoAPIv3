using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System;
using System.Web;
using System.Net;
using System.IO;

/*
  Sample C# app to move a card on the board.

  To use it, you'll need to modify it for your organization, project, story, cell id, username and password.
*/

namespace APITest
{
    class Program
    {
        private const string URL = "https://app.scrumdo.com/openapi/v3/organizations/demotest/projects/xxx2/stories/125344";
        private const string user = "username";
        private const string pass = "password";

        static void Main(string[] args)
        {
            String DATA = @"{""cell_id"":41033}";
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(URL);
            byte[] cred = UTF8Encoding.UTF8.GetBytes(user + ":" + pass);
            string base64 = Convert.ToBase64String(cred);
            string authorization = String.Concat("Basic ", base64);
            request.Headers.Add("Authorization", authorization);
            request.Method = "PUT";
            request.ContentType = "application/json";
            request.ContentLength = DATA.Length;
            using (Stream webStream = request.GetRequestStream())
            using (StreamWriter requestWriter = new StreamWriter(webStream, System.Text.Encoding.ASCII))
            {
                requestWriter.Write(DATA);
            }

            try {
                WebResponse webResponse = request.GetResponse();
                using (Stream webStream = webResponse.GetResponseStream())
                {
                    if (webStream != null)
                    {
                        using (StreamReader responseReader = new StreamReader(webStream))
                        {
                            string response = responseReader.ReadToEnd();
                            Console.WriteLine(response);
                        }
                    }
                }
            }
            catch (Exception e)
            {
                Console.WriteLine("-----------------");
                Console.WriteLine(e.Message);

            }
        }
    }
}
