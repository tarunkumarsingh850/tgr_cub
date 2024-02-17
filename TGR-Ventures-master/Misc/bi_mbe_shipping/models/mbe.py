import requests
import requests


url = "https://api.mbeonline.es/ws/e-link.wsdl"
headers = {"content-type": "text/xml"}
CHANGE_STATE_BODY = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                        xmlns:ws="http://www.onlinembe.eu/ws/">
            <soapenv:Header/>
            <soapenv:Body>
                <ws:ShipmentRequest>
                    <RequestContainer>
                        <Credentials> *Las credenciales no han de enviarse en cada
                        llamada, sinó que se debe usar una autenticación básica.
                        <Username>tiger-one-test.es0999.mol@Spain</Username>
                        <Passphrase>tu7B3knjWkwnehSgCW0EXg6tSsiLoda7</Passphrase>
                        </Credentials>
                        <InternalReferenceID>XXXXXXX</InternalReferenceID>
                        <Recipient>
                        <Name>XXXXXXX</Name>
                        <CompanyName>XXXXXXX</CompanyName>
                        <Address>XXXXXXX</Address>
                        <Phone>XXXXXXX</Phone>
                        <ZipCode>XXXXXXX</ZipCode>
                        <City>XXXXXXX</City>
                        <State>ISO CODE 2</State> -> Campo opcional, pero obligatorio para EEUU,
                        Canadá, Emiratos Árabes y México. Se expresa en código ISO de 2 caracteres.
                        <Country>ISO CODE 2</Country>
                        <Email/>
                        </Recipient>
                        <Shipment>
                        <ShipperType>MBE</ShipperType>
                        <Description>XXXXXXX</Description>
                        <COD>true/ false</COD>
                        <Insurance>true/ false</Insurance>
                        <PackageType>DOCUMENTS| ENVELOPE | GENERIC</PackageType> -> Establecer "GENERIC" para paquetería
                        <Service>SEE| SSE</Service> Servicio Exprés o Servicio Standard
                        <Referring>XXXXXXX</Referring>
                        <Items>
                            <Item>
                                <Weight>Acepta decimal expresado en kg</Weight>
                                <Dimensions>
                                    <Lenght>Acepta decimal expresado en cm</Lenght>
                                    <Height>Acepta decimal expresado en cm</Height>
                                    <Width>Acepta decimal expresado en cm</Width>
                                </Dimensions>
                            </Item>
                        </Items>
                        <!--Opcional-->
                        <ProformaInvoice>
                            <ProformaDetail>
                                <Amount>1</Amount> -> Cantidad de productos
                                <Currency>EUR</Currency> -> Moneda
                                <Value>1.00</Value> -> Valor mercancía
                                <Unit>PCS</Unit> -> Unidad, "PCS" para piezas
                                <Description>XXXXXXX</Description> -> Descripción producto
                            </ProformaDetail>
                        </ProformaInvoice>
                        <!--Opcional-->
                        <Products>
                            <!--1 o más repeticiones-->
                            <Product>
                                <SKUCode>XXXXXXX</SKUCode>
                                <Description>XXXXXXX</Description>
                                <Quantity>XXXXXXX</Quantity>
                            </Product>
                        </Products>
                        <Notes>XXXXXXX</Notes>
                        </Shipment>
                    </RequestContainer>
                </ws:ShipmentRequest>
            </soapenv:Body>
            </soapenv:Envelope>"""


response = requests.post(url, data=CHANGE_STATE_BODY, headers=headers)
print(response.content)
