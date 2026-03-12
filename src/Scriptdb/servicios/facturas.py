"""
Proyecto ODIN - Generador de servicios api-rest  
Módulo: Generador reportes Api-rest
Basado en framework Flask
Author: Jairol Lavado.
Fecha: Enero 2024
versión: 0.0.0.1
"""
import json

def consultaRegistros(conexion,busqueda):
    try:
        with conexion.cursor() as cursor:
            query = """
                    SELECT 
                        JSON_OBJECT(
                        'Document' VALUE JSON_OBJECT(
                            'EXT' VALUE JSON_OBJECT(
                                'InvoiceAuthorization' VALUE RES_INVOICE_AUTHORIZATION,
                                'StartDate' VALUE TO_CHAR(RES_START_DATE,'YYYY-MM-DD'),
                                'EndDate' VALUE TO_CHAR(RES_END_DATE,'YYYY-MM-DD'),
                                'Prefix' VALUE RES_PREFIX,
                                'From' VALUE RES_FROM,
                                'To' VALUE RES_TO,
                                'IdentificationCode' VALUE TO_CHAR(CD_IDENTIFICATION_CODE),
                                'ProviderID' VALUE TO_CHAR(CD_PROVIDER_ID),
                                'ProviderID_schemeID' VALUE TO_CHAR(CD_PROVIDER_ID_SCHEME_ID),
                                'SoftwareID' VALUE TO_CHAR(CD_SOFTWARE_ID),
                                'SoftwareSecurityCode' VALUE TO_CHAR(CD_SOFTWARE_SECURITY_CODE),
                                'AuthorizationProviderID' VALUE TO_CHAR(CD_AUTHORIZATION_PROVIDER_ID),
                                'AuthorizationProviderID_schemeID' VALUE TO_CHAR(CD_AUTHORIZATION_PROVIDER_ID_SCHEME_ID),
                                'QRCode' VALUE TO_CHAR(CD_SOFTWARE_SECURITY_CODE) 
                            ),
                            'NOT' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'Note' VALUE 'OBSERVACIONES'
                                    ),
                                    JSON_OBJECT(
                                        'Note' VALUE 'VENDEDOR'
                                    ),
                                    JSON_OBJECT(
                                        'Note' VALUE 'CENTRO DE COSTO'
                                    ),
                                    JSON_OBJECT(
                                        'Note' VALUE 'Pago por Transferencia Bancaria al Banco de Occidente, Cuenta de ahorros No. 230-81461-8'
                                    )
                                ),
                            'FAC' VALUE JSON_OBJECT(
                                    'UBLVersionID' VALUE EF_UBL_VERSION_ID,
                                    'CustomizationID' VALUE TO_CODE,
                                    'ProfileID' VALUE EF_PROFILE_ID,
                                    'ProfileExecutionID' VALUE EF_PROFILE_EXECUTION_ID,
                                    'ID' VALUE FAC_DOCUMENT_ID,
                                    'UUID' VALUE FAC_UUID,
                                    'IssueDate' VALUE TO_CHAR(FAC_ISSUE_DATE, 'YYYY-MM-DD'),
                                    'IssueTime' VALUE TO_CHAR(FAC_ISSUE_DATE, 'HH24:MI:SS'),
                                    'InvoiceTypeCode' VALUE FAC_DOCUMENT_TYPE_ID,
                                    'DocumentCurrencyCode' VALUE EF_DOCUMENT_CURRENCY_CODE,
                                    'LineCountNumeric' VALUE FAC_LINE_COUNT_NUMERIC
                            ),
                            'ASP' VALUE JSON_OBJECT(
                                    'AdditionalAccountID' VALUE EMF_ADDITIONAL_ACCOUNT_ID,
                                    'PartyName' VALUE EMF_PARTY_NAME,
                                    'Physical_ADD_ID' VALUE 1,
                                    'Tax_RegistrationName' VALUE EMF_TAX_REGISTRATION_NAME,
                                    'Tax_CompanyID' VALUE EMF_TAX_COMPANY_ID,
                                    'Tax_CompanyID_schemeName' VALUE EMF_TAX_COMPANY_SCHEME_NAME_ID,
                                    'Tax_LevelCode' VALUE erf.RF_CODE,
                                    'Tax_LevelCode_listName' VALUE EMF_TAX_LEVEL_LIST_NAME,
                                    'Tax_Scheme_ID' VALUE EMF_TAX_SCHEME_ID,
                                    'Tax_Scheme_Name' VALUE EMF_TAX_SCHEME_NAME,
                                    'Registration_ADD_ID' VALUE 1,
                                    'Contact_ID' VALUE 1
                                ),
                                'ACP' VALUE JSON_OBJECT(
                                    'AdditionalAccountID' VALUE RCF_ADDITIONAL_ACCOUNT_ID,
                                    'PartyName' VALUE RCF_PARTY_NAME,
                                    'Physical_ADD_ID' VALUE 2,
                                    'Tax_RegistrationName' VALUE RCF_TAX_REGISTRATION_NAME,
                                    'Tax_CompanyID' VALUE RCF_TAX_COMPANY_ID,
                                    'Tax_CompanyID_schemeName' VALUE RCF_TAX_COMPANY_SCHEME_NAME_ID,
                                    'Tax_LevelCode' VALUE rrf.RF_CODE,
                                    'Tax_LevelCode_listName' VALUE RCF_TAX_LEVEL_CODE_LIST_NAME,
                                    'Tax_Scheme_ID' VALUE RCF_TAX_SCHEME_ID,
                                    'Tax_Scheme_Name' VALUE RCF_TAX_SCHEME_NAME,
                                    'Registration_ADD_ID' VALUE 2,
                                    'Contact_ID' VALUE 2
                                ),
                                'PYM' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'ID' VALUE PAG_FORM_ID,
                                        'PaymentMeansCode' VALUE PAG_PAYMENT_MEANS_ID,
                                        'PaymentDueDate' VALUE PAG_PAYMENT_DUE_DATE
                                    )
                                ),
                                'TOT' VALUE JSON_OBJECT(
                                    'LineExtensionAmount' VALUE TOTF_LINE_EXTENSION_AMOUNT,
                                    'TaxExclusiveAmount' VALUE TOTF_TAX_EXCLUSIVE_AMOUNT,
                                    'TaxInclusiveAmount' VALUE TOTF_TAX_INCLUSIVE_AMOUNT,
                                    'PayableAmount' VALUE TOTF_PAYABLE_AMOUNT
                                ),
                                'IVL' VALUE (
                                    SELECT JSON_ARRAYAGG(
                                        JSON_OBJECT(
                                            'ID' VALUE df.DF_LINE_ID,
                                            'InvoicedQuantity' VALUE df.DF_QUANTITY,
                                            'InvoicedQuantityUnitCode' VALUE dfum.UM_CODE,
                                            'LineExtensionAmount' VALUE df.DF_LINE_EXTENSION_AMOUNT,
                                            'PriceAmount' VALUE df.DF_PRICE_AMOUNT,
                                            'BaseQuantity' VALUE df.DF_BASE_QUANTITY,
                                            'BaseQuantity_unitCode' VALUE dfum.UM_CODE,
                                            'Item_Description' VALUE df.DF_ITEM_DESCRIPTION,
                                            'Standard_ItemID' VALUE dfit.ITEM_CODE,
                                            'Standard_ItemID_SchemeID' VALUE dfpro.PR_SCHEME_NAME
                                        )
                                    )
                                    FROM MNTFE.FEDETALLE df
                                    JOIN MNTFE.FEUNIDADMEDIDA dfum 
                                        ON dfum.UM_ID = df.DF_QUANTITY_UNIT_ID
                                    JOIN MNTFE.FEITEM dfit 
                                        ON dfit.ITEM_ID = df.DF_STANDARD_ITEM_ID
                                    JOIN MNTFE.FEPRODUCTO dfpro 
                                        ON dfpro.PR_ID = df.DF_STANDARD_ITEM_ID_SCHEME_ID
                                    WHERE df.DF_SECUENCIA = fac.FAC_SECUENCIA
                                    AND df.DF_SECUENCIA_ANO = fac.FAC_SECUENCIA_ANO
                                ),
                                'REC' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'Nombre' VALUE REC_NAME,
                                        'Email' VALUE REC_EMAIL,
                                        'Enviar_Email' VALUE (
                                            CASE REC_SEND_EMAIL
                                                WHEN 'S' THEN 'true'
                                                WHEN 'N' THEN 'false'
                                                ELSE 'null'
                                            END
                                        ) FORMAT JSON,
                                        'Incluir_Anexos' VALUE (
                                            CASE REC_INCLUDE_ATTACHMENTS
                                                WHEN 'S' THEN 'true'
                                                WHEN 'N' THEN 'false'
                                                ELSE 'null'
                                            END
                                        ) FORMAT JSON,
                                        'Incluir_PDF' VALUE (
                                            CASE REC_INCLUDE_PDF
                                                WHEN 'S' THEN 'true'
                                                WHEN 'N' THEN 'false'
                                                ELSE 'null'
                                            END
                                        ) FORMAT JSON,
                                        'Incluir_XML' VALUE (
                                            CASE REC_INCLUDE_XML
                                                WHEN 'S' THEN 'true'
                                                WHEN 'N' THEN 'false'
                                                ELSE 'null'
                                            END
                                        ) FORMAT JSON
                                    )
                                ),
                                'ADD' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                            'ID' VALUE 1,
                                            'CityID' VALUE emf.EMF_CM_ID,
                                            'CityName' VALUE ecm.CM_CITY_NAME,
                                            'PostalZone' VALUE 111611,
                                            'CountrySubentity' VALUE emfDm.DM_DEPARTMENT_NAME,
                                            'CountrySubentityCode' VALUE emfDm.DM_ID,
                                            'AddressLine' VALUE emf.EMF_ADDRESS_LINE,
                                            'CountryName' VALUE emfp.PA_DESCRIPCION,
                                            'CountryCode' VALUE emfp.PA_CODE
                                    ),
                                    JSON_OBJECT(
                                            'ID' VALUE 2,
                                            'CityID' VALUE ADD_CM_ID,
                                            'CityName' VALUE addcm.CM_CITY_NAME,
                                            'PostalZone' VALUE '',
                                            'CountrySubentity' VALUE addDm.DM_DEPARTMENT_NAME,
                                            'CountrySubentityCode' VALUE addDm.DM_ID,
                                            'AddressLine' VALUE ADD_ADDRESS_LINE,
                                            'CountryName' VALUE addp.PA_DESCRIPCION,
                                            'CountryCode' VALUE addp.PA_CODE
                                    )
                                ),
                                'CON' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'ID' VALUE '1',
                                        'Name' VALUE emf.EMF_PARTY_NAME,
                                        'Telephone' VALUE emf.EMF_TELEPHONE,
                                        'ElectronicMail' VALUE emf.EMF_EMAIL 
                                    ),
                                    JSON_OBJECT(
                                        'ID' VALUE '2',
                                        'Name' VALUE CON_NAME,
                                        'Telephone' VALUE CON_TELEPHONE,
                                        'ElectronicMail' VALUE CON_EMAIL
                                    )
                                )
                        )
                        RETURNING CLOB
                        ) AS json_result
                        FROM MNTFE.FEFACTURA fac
                        INNER JOIN MNTFE.FERESOLUCION re ON re.RES_ID = fac.FAC_RF_ID 
                        INNER JOIN MNTFE.FECONFIGURACIONDIAN confd ON confd.CD_ID = re.RES_CONFIGURACION_ID
                        INNER JOIN MNTFE.FETIPOOPERACION fto ON fto.TO_ID = fac.FAC_CUSTOMIZATION_ID  
                        INNER JOIN MNTFE.FETIPODOCUMENTO ftd ON ftd.TD_ID = fac.FAC_DOCUMENT_TYPE_ID   
                        INNER JOIN MNTFE.FEENCABEZADO encf ON encf.EF_ID = fac.FAC_EF_ID 
                        INNER JOIN MNTFE.FEAMBIENTEDESTINO ad ON ad.AD_ID = encf.EF_PROFILE_EXECUTION_ID   
                        INNER JOIN MNTFE.FEEMISOR emf ON emf.EMF_ID = fac.FAC_EMF_ID   
                        INNER JOIN MNTFE.FETIPOIDENTIFICACION eti ON eti.TI_ID = emf.EMF_TAX_COMPANY_SCHEME_NAME_ID 
                        INNER JOIN MNTFE.FERESPONSABILIDADFISCAL erf ON erf.RF_ID = emf.EMF_TAX_LEVEL_ID 
                        INNER JOIN MNTFE.FETIPOPERSONA etp ON etp.TP_ID = emf.EMF_ADDITIONAL_ACCOUNT_ID 
                        INNER JOIN MNTFE.FEPAIS emfp ON emfp.PA_ID = emf.EMF_COUNTRY_ID
                        INNER JOIN MNTFE.FECIUDADMUNICIPIO ecm ON ecm.CM_ID = emf.EMF_CM_ID 
                        INNER JOIN MNTFE.FEDEPARTAMENTO emfDm ON emfDm.DM_ID = ecm.CM_DM_ID 
                        INNER JOIN MNTFE.FERECEPTOR recf ON recf.RCF_SECUENCIA  = fac.FAC_SECUENCIA AND recf.RCF_SECUENCIA_ANO = fac.FAC_SECUENCIA_ANO     
                        INNER JOIN MNTFE.FETIPOIDENTIFICACION rti ON rti.TI_ID = recf.RCF_TAX_COMPANY_SCHEME_NAME_ID  
                        LEFT JOIN MNTFE.FERESPONSABILIDADFISCAL rrf ON rrf.RF_ID = recf.RCF_TAX_LEVEL_ID  
                        INNER JOIN MNTFE.FETIPOPERSONA rtp ON rtp.TP_ID = recf.RCF_ADDITIONAL_ACCOUNT_ID
                        INNER JOIN MNTFE.FETOTALFACTURA totf ON totf.TOTF_SECUENCIA = fac.FAC_SECUENCIA AND totf.TOTF_SECUENCIA_ANO  = fac.FAC_SECUENCIA_ANO
                        INNER JOIN MNTFE.FEPAGO pagf ON pagf.PAG_SECUENCIA  = fac.FAC_SECUENCIA AND pagf.PAG_SECUENCIA_ANO   = fac.FAC_SECUENCIA_ANO
                        INNER JOIN MNTFE.FEFORMAPAGO pfp ON pfp.FPAG_ID = pagf.PAG_FORM_ID 
                        LEFT JOIN MNTFE.FEMEDIOPAGO pmp ON pmp.MPAG_ID = pagf.PAG_PAYMENT_MEANS_ID  
                        INNER JOIN MNTFE.FEDIRECCION addf ON addf.ADD_SECUENCIA = fac.FAC_SECUENCIA AND addf.ADD_SECUENCIA_ANO = fac.FAC_SECUENCIA_ANO
                        INNER JOIN MNTFE.FEPAIS addp ON addp.PA_ID = addf.ADD_COUNTRY_ID
                        INNER JOIN MNTFE.FECIUDADMUNICIPIO addcm ON addcm.CM_ID = addf.ADD_CM_ID 
                        INNER JOIN MNTFE.FEDEPARTAMENTO addDm ON addDm.DM_ID = addcm.CM_DM_ID 
                        INNER JOIN MNTFE.FECONTACTO conf ON conf.CON_SECUENCIA  = fac.FAC_SECUENCIA AND conf.CON_SECUENCIA_ANO  = fac.FAC_SECUENCIA_ANO
                        INNER JOIN MNTFE.FERECEPTORNOTIFICACION recnotf ON recnotf.REC_SECUENCIA  = fac.FAC_SECUENCIA AND recnotf.REC_SECUENCIA_ANO = fac.FAC_SECUENCIA_ANO
                        WHERE fac.FAC_SECUENCIA = :secuencia AND fac.FAC_SECUENCIA_ANO = :vigencia
                """
        params = {
            "secuencia": int(busqueda.get("secuencia", 0)),
            "vigencia": int(busqueda.get("vigencia", 0))
        }
        #print(query)
        #print(params)
        try:
            with conexion.cursor() as cursor:
                cursor.execute(query, params)
                fields = [field_md[0] for field_md in cursor.description]
                rows = cursor.fetchall()
                registros = [dict(zip(fields, row)) for row in rows]

            if registros:
                return {
                    "exec": True,
                    "data": registros
                }
            else:
                return {
                    "exec": False,
                    "data": [],
                    "message": "No se encontraron registros"
                }

        except Exception as e:
            print("Ocurrió un error al ejecutar la consulta de la factura:", e)
            return {
                "exec": False,
                "error": str(e)
            }

    except Exception as e:
        print("Ocurrió un error al consultar los APIs de reportes:", e)
        return {
            "exec": False,
            "error": str(e)
        }

def registroEnvio(conexion, datos):
    query = """
        INSERT INTO MNTFE.FEENVIO
        (
            ENV_SECUENCIA,
            ENV_SECUENCIA_ANO,
            ENV_DATE,
            ENV_STATE,
            ENV_TR_ID,
            ENV_QR
        )
        VALUES
        (
            :secuencia,
            :vigencia,
            SYSDATE,
            :estado,
            :id_transaccion,
            :qr_cod
        )
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "qr_cod": datos.get("qr_cod")
    }
    #print(query)
    #print(params)
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            conexion.commit()
        response = {
            "exec": True,
            "data": params
        }
        return response
    except Exception as e:
        print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def registroCUFE(conexion, datos):
    query = """
        UPDATE MNTFE.FEFACTURA
        SET FAC_UUID=:cufe
        WHERE 
        FAC_SECUENCIA=:secuencia
        AND FAC_SECUENCIA_ANO=:vigencia
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "cufe": str(datos.get("cufe", ""))
    }
    #print(query)
    #print(params)
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            conexion.commit()
        response = {
            "exec": True,
            "data": params
        }
        return response
    except Exception as e:
        print("Ocurrió un error al ejecutar la actualización:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response


def consultaReporte(conexion,query,busqueda):
    try:
        cursor = conexion.cursor()
        cursor.execute(query)
        # fetchone trae uno por uno todas las filas ## servicios = cursor.fetchone()
        # retorna alias y valores
        fields = [field_md[0] for field_md in cursor.description]
        registros = [dict(zip(fields,row)) for row in cursor.fetchall()]
        #cursor.close()
        #conexion.close()
        return registros
    except Exception as e:
        print("Ocurrió un error al consultar los reportes: ", e)
        return ''
    finally:
        cursor.close()

def executeReporte(conexion,query,busqueda):
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query)
            conexion.commit() 
            datos_actualizados = cursor.fetchone()  # O fetchall() si esperas múltiples filas
            registros = {}
            if datos_actualizados:
                fields = [field_md[0] for field_md in cursor.description]
                for campo, dato in zip(fields, datos_actualizados):
                    registros[campo] = dato
            response= { "exec" : True, "data": registros}
            return response 
    except Exception as e:
        print("Ocurrió un error al ejecutar la inserción: ", e)
        response= { "exec" : False}
        return response  # Indicador de fallo
    finally:
        cursor.close()



    try:
        with conexion.cursor() as cursor:
            searchQuery =  query
            print(query)
            cursor.execute(searchQuery)
            # fetchone trae uno por uno todas las filas ## servicios = cursor.fetchone()
            # retorna alias y valores
            fields = [field_md[0] for field_md in cursor.description]
            registros = [dict(zip(fields,row)) for row in cursor.fetchall()]
            #cursor.close()
            #conexion.close()
            return registros
    except Exception as e:
        print("Ocurrió un error al consultar los reportes: ", e)
        return ''
    finally:
        cursor.close()