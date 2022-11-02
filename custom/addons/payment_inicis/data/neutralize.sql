-- disable inicis payment provider
UPDATE payment_provider
   SET inicis_merchant_id = NULL,
       inicis_secure_hash_secret = NULL;
