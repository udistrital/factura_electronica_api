import json
from datetime import datetime

def consultaRegistros(conexion,busqueda):
    try:
        with conexion.cursor() as cursor:
            query = """
                    SELECT 
                        JSON_OBJECT(
                        'Document' VALUE JSON_OBJECT(
                        	'EXT' VALUE JSON_OBJECT(
                                'InvoiceAuthorization' VALUE TO_NUMBER(RES_INVOICE_AUTHORIZATION),
                                'StartDate' VALUE TO_CHAR(RES_START_DATE,'YYYY-MM-DD'),
                                'EndDate' VALUE TO_CHAR(RES_END_DATE,'YYYY-MM-DD'),
                                'Prefix' VALUE TO_CHAR(RES_PREFIX),
                                'From' VALUE RES_FROM,
                                'To' VALUE RES_TO,
                                'IdentificationCode' VALUE TO_CHAR(CD_IDENTIFICATION_CODE),
                                'ProviderID' VALUE TO_CHAR(CD_PROVIDER_ID),
                                'ProviderID_schemeID' VALUE TO_CHAR(CD_PROVIDER_ID_SCHEME_ID),
                                'SoftwareID' VALUE TO_CHAR(CD_SOFTWARE_ID),
                                'SoftwareSecurityCode': '""' FORMAT JSON,
                                'AuthorizationProviderID' VALUE TO_CHAR(CD_AUTHORIZATION_PROVIDER_ID),
                                'AuthorizationProviderID_schemeID' VALUE TO_CHAR(CD_AUTHORIZATION_PROVIDER_ID_SCHEME_ID),
                                'QRCode' : '""' FORMAT JSON
                            ),             
                            'FAC' VALUE JSON_OBJECT(
                                    'UBLVersionID' VALUE EF_UBL_VERSION_ID,
                                    'CustomizationID' VALUE TO_CODE,
                                    'ProfileID' VALUE EF_PROFILE_ID,
                                    'ProfileExecutionID' VALUE TO_CHAR(EF_PROFILE_EXECUTION_ID),
                                    'ID' VALUE FAC_DOCUMENT_ID,
                                    'UUID' VALUE NVL(TO_CHAR(FAC_UUID), ''),
                                    'IssueDate' VALUE TO_CHAR(SYSDATE, 'YYYY-MM-DD'),
                                    'IssueTime' VALUE TO_CHAR(SYSDATE, 'HH24:MI:SS'),
                                    'InvoiceTypeCode' VALUE TO_CHAR(FAC_DOCUMENT_TYPE_ID, 'FM00'),
                                    'DocumentCurrencyCode' VALUE EF_DOCUMENT_CURRENCY_CODE,
                                    'LineCountNumeric' VALUE FAC_LINE_COUNT_NUMERIC
                            ),
                            'NOT' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'Note' VALUE FAC_NOTE1
                                    ),
                                    JSON_OBJECT(
                                        'Note' : '""' FORMAT JSON
                                    ),
                                    JSON_OBJECT(
                                        'Note' VALUE NVL(TO_CHAR(FAC_COST_CENTER), '')
                                    ),
                                    JSON_OBJECT(
                                        'Note' VALUE FAC_NOTE4
                                    )
                            ),
						    'ORD' VALUE JSON_OBJECT(
						      'ID': '""' FORMAT JSON
						    ),
                            'ASP' VALUE JSON_OBJECT(
                                    'AdditionalAccountID' VALUE TO_CHAR(EMF_ADDITIONAL_ACCOUNT_ID),
                                    'PartyName' VALUE TO_CHAR(EMF_PARTY_NAME),
                                    'Physical_ADD_ID' VALUE '1',
                                    'Tax_RegistrationName' VALUE TO_CHAR(EMF_TAX_REGISTRATION_NAME),
                                    'Tax_CompanyID' VALUE TO_CHAR(EMF_TAX_COMPANY_ID),
      								'Tax_CompanyID_schemeID': '7',
                                    'Tax_CompanyID_schemeName' VALUE TO_CHAR(EMF_TAX_COMPANY_SCHEME_NAME_ID),
                                    'Tax_LevelCode' VALUE TO_CHAR(erf.RF_CODE),
                                    'Tax_LevelCode_listName': '""' FORMAT JSON,
                                    'Tax_Scheme_ID' VALUE TO_CHAR(EMF_TAX_SCHEME_ID, 'FM00'),
                                    'Tax_Scheme_Name' VALUE TO_CHAR(EMF_TAX_SCHEME_NAME),
                                    'Registration_ADD_ID' VALUE '1',
                                    'CorporateRegistrationScheme_ID': '""' FORMAT JSON,
                                    'Contact_ID' VALUE '1',
                                    'SellerContact_ID': '""' FORMAT JSON
                                ),
                            'ACP' VALUE JSON_OBJECT(
                            		'CustomerAssignedAccountID': '""' FORMAT JSON,
                                    'AdditionalAccountID' VALUE TO_CHAR(RCF_ADDITIONAL_ACCOUNT_ID),
                                    'PartyName' VALUE TO_CHAR(RCF_PARTY_NAME),
                                    'Physical_ADD_ID' VALUE '2',
                                    'Tax_RegistrationName' VALUE TO_CHAR(RCF_TAX_REGISTRATION_NAME),
                                    'Tax_CompanyID' VALUE TO_CHAR(RCF_TAX_COMPANY_ID),
                                    'Tax_CompanyID_schemeName' VALUE TO_CHAR(RCF_TAX_COMPANY_SCHEME_NAME_ID),
                                    'Tax_LevelCode' VALUE NVL(TO_CHAR(rrf.RF_CODE), ''),
                                    'Tax_LevelCode_listName' VALUE NVL(TO_CHAR(RCF_TAX_LEVEL_CODE_LIST_NAME), ''),
                                    'Tax_Scheme_ID' VALUE TO_CHAR(RCF_TAX_SCHEME_ID, 'FM00'),
                                    'Tax_Scheme_Name' VALUE TO_CHAR(RCF_TAX_SCHEME_NAME),
                                    'Registration_ADD_ID' VALUE '2',
                                    'Contact_ID' VALUE '2'
                                ),
                            'PYM' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'ID' VALUE TO_CHAR(PAG_FORM_ID),
                                        'PaymentMeansCode' VALUE NVL(TO_CHAR(PAG_PAYMENT_MEANS_ID), ''),
                                        'PaymentDueDate' VALUE NVL(TO_CHAR(PAG_PAYMENT_DUE_DATE,'YYYY-MM-DD'), TO_CHAR(SYSDATE, 'YYYY-MM-DD')), 
                                        'InstructionNote': '""' FORMAT JSON,
                                        'PaymentID': '""' FORMAT JSON
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
                                            'ID' VALUE TO_CHAR(df.DF_LINE_ID),
                                    		'UUID' VALUE NVL(TO_CHAR(FAC_UUID), ''),
                                    		'Note': '""' FORMAT JSON,
                                            'InvoicedQuantity' VALUE df.DF_QUANTITY,
                                            'InvoicedQuantityUnitCode' VALUE TO_CHAR(dfum.UM_CODE),
                                            'LineExtensionAmount' VALUE df.DF_LINE_EXTENSION_AMOUNT,
                                            'PriceAmount' VALUE df.DF_PRICE_AMOUNT,
                                            'BaseQuantity' VALUE df.DF_BASE_QUANTITY,
                                            'BaseQuantity_unitCode' VALUE TO_CHAR(dfum.UM_CODE),
                                            'Item_Description' VALUE TO_CHAR(df.DF_ITEM_DESCRIPTION),
                                            'Standard_ItemID' VALUE TO_CHAR(dfit.ITEM_CODE),
                                            'Standard_ItemID_SchemeID' VALUE TO_CHAR(dfpro.PR_ID, 'FM000'),
                                            'Standard_ItemID_SchemeName' VALUE TO_CHAR(dfpro.PR_SCHEME_NAME),
       	 									'Standard_ItemID_SchemeAgencyID' VALUE TO_CHAR(dfpro.PR_SCHEME_AGENCY_ID)
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
                                        'Nombre' VALUE TO_CHAR(REC_NAME),
                                        'Email' VALUE TO_CHAR(REC_EMAIL),
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
                                            'ID' VALUE '1',
                                            'CityID' VALUE TO_CHAR(emf.EMF_CM_ID),
                                            'CityName' VALUE UPPER(ecm.CM_CITY_NAME),
                                            'PostalZone' VALUE  TO_CHAR(emf.EMF_POSTAL_ZONE),
                                            'CountrySubentity' VALUE UPPER(emfDm.DM_DEPARTMENT_NAME),
                                            'CountrySubentityCode' VALUE TO_CHAR(emfDm.DM_ID),
                                            'AddressLine' VALUE TO_CHAR(emf.EMF_ADDRESS_LINE),
                                            'CountryName' VALUE UPPER(emfp.PA_DESCRIPCION),
                                            'CountryCode' VALUE TO_CHAR(emfp.PA_CODE)
                                    ),
                                    JSON_OBJECT(
                                            'ID' VALUE '2',
                                            'CityID' VALUE TO_CHAR(ADD_CM_ID),
                                            'CityName' VALUE UPPER(addcm.CM_CITY_NAME),
                                            'PostalZone' VALUE NVL(addf.ADD_POSTAL_ZONE, '""') FORMAT JSON,
                                            'CountrySubentity' VALUE UPPER(addDm.DM_DEPARTMENT_NAME),
                                            'CountrySubentityCode' VALUE TO_CHAR(addDm.DM_ID),
                                            'AddressLine' VALUE TO_CHAR(ADD_ADDRESS_LINE),
                                            'CountryName' VALUE UPPER(addp.PA_DESCRIPCION),
                                            'CountryCode' VALUE TO_CHAR(addp.PA_CODE)
                                    )
                                ),
                            'CON' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'ID' VALUE '1',
                                        'Name' VALUE TO_CHAR(emf.EMF_PARTY_NAME),
                                        'Telephone' VALUE TO_CHAR(emf.EMF_TELEPHONE),
                                        'ElectronicMail' VALUE TO_CHAR(emf.EMF_EMAIL),
                                        'Note': '""' FORMAT JSON
                                    ),
                                    JSON_OBJECT(
                                        'ID' VALUE '2',
                                        'Name' VALUE TO_CHAR(CON_NAME),
                                        'Telephone' VALUE TO_CHAR(CON_TELEPHONE),
                                        'ElectronicMail' VALUE TO_CHAR(CON_EMAIL),
                                        'Note': '""' FORMAT JSON
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
            #print("Ocurrió un error al ejecutar la consulta de la factura:", e)
            return {
                "exec": False,
                "error": str(e)
            }

    except Exception as e:
        #print("Ocurrió un error al consultar los APIs de reportes:", e)
        return {
            "exec": False,
            "error": str(e)
        }

def consultaEnvio(conexion, datos):
    query = """
        SELECT 
            ENV_ID,
            ENV_SECUENCIA, 
            ENV_SECUENCIA_ANO, 
            ENV_DATE,
            ENV_STATE_SEND,
            ENV_TR_ID,
            ENV_ERROR,
            ENV_STATE
        FROM MNTFE.FEENVIO
        WHERE
        ENV_SECUENCIA = :secuencia
        AND ENV_SECUENCIA_ANO = :vigencia
        AND ENV_STATE='A'
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0))
    }
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query, params)
            fields = [field_md[0] for field_md in cursor.description]
            rows = cursor.fetchall()
            registros = [dict(zip(fields, row)) for row in rows]
        if registros:
            return {"exec": True,"data": registros }
        else:
            return {"exec": False, "data": [], "message": "No se encontraron registros" }
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def registroEnvio(conexion, datos):
    query = """
        INSERT INTO MNTFE.FEENVIO
        (
            ENV_SECUENCIA, 
            ENV_SECUENCIA_ANO, 
            ENV_DATE, 
            ENV_STATE_SEND, 
            ENV_TR_ID,  
            ENV_ERROR, 
            ENV_STATE
        )
        VALUES
        (   :secuencia,
            :vigencia,
            SYSDATE,
            :estado,
            :id_transaccion,
            :error_msg,
            'A'
        )
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "error_msg":str(datos.get("error_emision", "")),
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
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def registroEnvioOLD(conexion, datos):
    query = """
        INSERT INTO MNTFE.FEENVIO
        (
            ENV_ID,
            ENV_SECUENCIA, 
            ENV_SECUENCIA_ANO, 
            ENV_DATE, 
            ENV_STATE_SEND, 
            ENV_TR_ID,  
            ENV_ERROR, 
            ENV_STATE
        )
        VALUES
        (   (SELECT NVL(MAX(ENV_ID), 0) + 1 AS NEXT_ID
              FROM MNTFE.FEENVIO), 
            :secuencia,
            :vigencia,
            SYSDATE,
            :estado,
            :id_transaccion,
            :error_msg,
            'A'
        )
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "error_msg":str(datos.get("error_emision", "")),
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
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response


def consultaSolicitudes(conexion, datos):
    query = """
        SELECT 
            ENV_ID,
            ENV_SECUENCIA, 
            ENV_SECUENCIA_ANO, 
            ENV_DATE,
            ENV_STATE_SEND,
            ENV_TR_ID,
            ENV_ERROR,
            ENV_STATE
        FROM MNTFE.FEENVIO
        WHERE
        ENV_STATE='A'
        AND ENV_STATE_SEND='S'
    """
    try:
        with conexion.cursor() as cursor:
            cursor.execute(query)
            fields = [field_md[0] for field_md in cursor.description]
            rows = cursor.fetchall()
            registros = [dict(zip(fields, row)) for row in rows]
        if registros:
            return {"exec": True,"data": registros }
        else:
            return {"exec": False, "data": [], "message": "No se encontraron registros" }
    except Exception as e:
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response

def actualizaSolicitud(conexion, datos):
    query = """
        UPDATE MNTFE.FEENVIO
        SET 
        ENV_STATE_SEND = :estado
        , ENV_ERROR = :error_msg
        WHERE
        ENV_TR_ID = :id_transaccion
    """
    params = {
        "estado": str(datos.get("estado", "")),
        "id_transaccion": int(datos.get("id_transaccion", 0)) if datos.get("id_transaccion") not in [None, ""] else 0,
        "error_msg":str(datos.get("error_dian", "")),
    }
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




def actualizaEnvio(conexion, datos):
    query = """
        UPDATE MNTFE.FEENVIO
        SET ENV_STATE = 'I'
        WHERE
        ENV_SECUENCIA = :secuencia 
        AND ENV_SECUENCIA_ANO = :vigencia 
    """
    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0))
    }
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
        #print("Ocurrió un error al ejecutar la inserción del envio:", e)
        response = {
            "exec": False,
            "error": str(e)
        }
        return response



def registroCUFE(conexion, datos):
    query = """
        UPDATE MNTFE.FEFACTURA
        SET FAC_UUID=:cufe
        , FAC_QR=:qr_code
        , FAC_ISSUE_DATE=TO_DATE(:emision, 'YYYY-MM-DD HH24:MI:SS')
        WHERE 
        FAC_SECUENCIA=:secuencia
        AND FAC_SECUENCIA_ANO=:vigencia
    """

    fecha_raw = datos.get("fecha_emision")
    if fecha_raw:
        fecha_raw = str(fecha_raw).strip()
        if len(fecha_raw) >= 19:
            # Caso con zona horaria o completo
            fecha_emite = fecha_raw[:19]
        elif len(fecha_raw) == 10:
            # Solo fecha → completar hora
            fecha_emite = f"{fecha_raw} 00:00:00"
        else:
            # Formato inesperado
            fecha_emite = None
    else:
        fecha_emite = None

    params = {
        "secuencia": int(datos.get("secuencia", 0)),
        "vigencia": int(datos.get("vigencia", 0)),
        "cufe": str(datos.get("cufe", "")),
        "qr_code": str(datos.get("qr_cod", "")),
        "emision": fecha_emite
    }
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
        #print("Ocurrió un error al ejecutar la actualización:", e)
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
        #print("Ocurrió un error al consultar los reportes: ", e)
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
        #print("Ocurrió un error al ejecutar la inserción: ", e)
        response= { "exec" : False}
        return response  # Indicador de fallo
    finally:
        cursor.close()
