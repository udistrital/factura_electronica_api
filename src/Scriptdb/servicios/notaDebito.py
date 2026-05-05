import json
from datetime import datetime

def consultaCodigoNotaDeb(conexion, datos):
    query = """
        SELECT TD_DESCRIPTION, 
        TD_TR_TYPE_COD
        FROM MNTFE.FETIPODOCUMENTO
        WHERE LOWER(TD_DESCRIPTION) LIKE LOWER('Nota débito')
    """
    #print(query)
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

def consultaRegistrosNotaDeb(conexion,busqueda):
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
                            'DEB' VALUE JSON_OBJECT(
                                    'UBLVersionID' VALUE EF_UBL_VERSION_ID,
                                    'CustomizationID' VALUE TO_CODE,
                                    'ProfileID' VALUE EF_PROFILE_ID,
                                    'ProfileExecutionID' VALUE TO_CHAR(EF_PROFILE_EXECUTION_ID),
                                    'ID' VALUE nota.FAC_DOCUMENT_ID,
                                    'UUID' VALUE NVL(TO_CHAR(nota.FAC_UUID), ''),
                                    'IssueDate' VALUE TO_CHAR(SYSDATE, 'YYYY-MM-DD'),
                                    'IssueTime' VALUE TO_CHAR(SYSDATE, 'HH24:MI:SS'),
                                    'DocumentCurrencyCode' VALUE EF_DOCUMENT_CURRENCY_CODE,
                                    'LineCountNumeric' VALUE nota.FAC_LINE_COUNT_NUMERIC,
                                    'DiscrepancyResponseCode' VALUE TO_CHAR(razNot.RNOT_COD),
                                    'DiscrepancyResponseDescription' VALUE razNot.RNOT_DESCRIPTION 
                            ),
                            'NOT' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'Note' VALUE (nota.FAC_NOTE1 || ' / Razón de nota: ' || razNot.RNOT_DESCRIPTION )
                                    ),
                                    JSON_OBJECT(
                                        'Note' : '""' FORMAT JSON
                                    ),
                                    JSON_OBJECT(
                                        'Note' VALUE NVL(TO_CHAR(nota.FAC_COST_CENTER), '')
                                    ),
                                    JSON_OBJECT(
                                        'Note' VALUE nota.FAC_NOTE4
                                    )
                            ),
						    'ORD' VALUE JSON_OBJECT(
						      'ID': '""' FORMAT JSON
						    ),
						    'BRF' VALUE JSON_ARRAY(
                                    JSON_OBJECT(
                                        'Invoice_ID' VALUE facRef.FAC_DOCUMENT_ID,
                                        'Invoice_UUID' VALUE facRef.FAC_UUID,
                                        'Invoice_IssueDate' VALUE TO_CHAR(facRef.FAC_ISSUE_DATE,'YYYY-MM-DD')  
                                    )
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
                                    'Tax_CompanyID_schemeID' VALUE NVL(TO_CHAR(RCF_TAX_COMPANY_SCHEME_ID), ''),
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
                                        'PaymentDueDate' VALUE TO_CHAR(SYSDATE, 'YYYY-MM-DD'), 
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
                            'DNL' VALUE (
                                    SELECT JSON_ARRAYAGG(
                                        JSON_OBJECT(
                                            'ID' VALUE TO_CHAR(df.DF_LINE_ID),
                                    		'UUID' VALUE NVL(TO_CHAR(nota.FAC_UUID), ''),
                                    		'Note': '""' FORMAT JSON,
                                            'DebitedQuantity' VALUE df.DF_QUANTITY,
                                            'DebitedQuantityUnitCode' VALUE TO_CHAR(dfum.UM_CODE),
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
                                    WHERE df.DF_FAC_ID = nota.FAC_ID
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
                        FROM MNTFE.FEFACTURA nota
                        INNER JOIN MNTFE.FERESOLUCION re ON re.RES_ID = nota.FAC_RF_ID 
                        INNER JOIN MNTFE.FECONFIGURACIONDIAN confd ON confd.CD_ID = re.RES_CONFIGURACION_ID
                        INNER JOIN MNTFE.FETIPOOPERACION fto ON fto.TO_ID = nota.FAC_CUSTOMIZATION_ID  
                        INNER JOIN MNTFE.FETIPODOCUMENTO ftd ON ftd.TD_ID = nota.FAC_DOCUMENT_TYPE_ID   
                        INNER JOIN MNTFE.FEENCABEZADO encf ON encf.EF_ID = nota.FAC_EF_ID 
                        INNER JOIN MNTFE.FEAMBIENTEDESTINO ad ON ad.AD_ID = encf.EF_PROFILE_EXECUTION_ID   
                        INNER JOIN MNTFE.FEEMISOR emf ON emf.EMF_ID = nota.FAC_EMF_ID   
                        INNER JOIN MNTFE.FETIPOIDENTIFICACION eti ON eti.TI_ID = emf.EMF_TAX_COMPANY_SCHEME_NAME_ID 
                        INNER JOIN MNTFE.FERESPONSABILIDADFISCAL erf ON erf.RF_ID = emf.EMF_TAX_LEVEL_ID 
                        INNER JOIN MNTFE.FETIPOPERSONA etp ON etp.TP_ID = emf.EMF_ADDITIONAL_ACCOUNT_ID 
                        INNER JOIN MNTFE.FEPAIS emfp ON emfp.PA_ID = emf.EMF_COUNTRY_ID
                        INNER JOIN MNTFE.FECIUDADMUNICIPIO ecm ON ecm.CM_ID = emf.EMF_CM_ID 
                        INNER JOIN MNTFE.FEDEPARTAMENTO emfDm ON emfDm.DM_ID = ecm.CM_DM_ID 
                        INNER JOIN MNTFE.FERECEPTOR recf ON recf.RCF_FAC_ID = nota.FAC_ID     
                        INNER JOIN MNTFE.FETIPOIDENTIFICACION rti ON rti.TI_ID = recf.RCF_TAX_COMPANY_SCHEME_NAME_ID  
                        LEFT JOIN MNTFE.FERESPONSABILIDADFISCAL rrf ON rrf.RF_ID = recf.RCF_TAX_LEVEL_ID  
                        INNER JOIN MNTFE.FETIPOPERSONA rtp ON rtp.TP_ID = recf.RCF_ADDITIONAL_ACCOUNT_ID
                        INNER JOIN MNTFE.FETOTALFACTURA totf ON totf.TOTF_FAC_ID = nota.FAC_ID
                        INNER JOIN MNTFE.FEPAGO pagf ON pagf.PAG_FAC_ID  = nota.FAC_ID
                        INNER JOIN MNTFE.FEFORMAPAGO pfp ON pfp.FPAG_ID = pagf.PAG_FORM_ID 
                        LEFT JOIN MNTFE.FEMEDIOPAGO pmp ON pmp.MPAG_ID = pagf.PAG_PAYMENT_MEANS_ID  
                        INNER JOIN MNTFE.FEDIRECCION addf ON addf.ADD_FAC_ID = nota.FAC_ID
                        INNER JOIN MNTFE.FEPAIS addp ON addp.PA_ID = addf.ADD_COUNTRY_ID
                        INNER JOIN MNTFE.FECIUDADMUNICIPIO addcm ON addcm.CM_ID = addf.ADD_CM_ID 
                        INNER JOIN MNTFE.FEDEPARTAMENTO addDm ON addDm.DM_ID = addcm.CM_DM_ID 
                        INNER JOIN MNTFE.FECONTACTO conf ON conf.CON_FAC_ID  = nota.FAC_ID
                        INNER JOIN MNTFE.FERECEPTORNOTIFICACION recnotf ON recnotf.REC_FAC_ID  = nota.FAC_ID
                        INNER JOIN MNTFE.FEFACTURA facRef ON facRef.FAC_ID  = nota.FAC_REFERENCE_ID 
                        LEFT JOIN MNTFE.FERAZONNOTA razNot ON nota.FAC_RNOT_ID = razNot.RNOT_ID                   
                        WHERE nota.FAC_CUSTOMIZATION_ID = 3 
                        AND nota.FAC_ID = :notaDebito
                """
        params = {
                "notaDebito": int(busqueda.get("id_factura", 0))
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