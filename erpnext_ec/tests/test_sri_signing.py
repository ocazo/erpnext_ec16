"""Regression tests for the native XAdES signer (xades_tool_v4).

Uses a self-signed certificate generated on the fly, so no real .p12 is needed.
"""

import base64
import datetime
import hashlib

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID
from frappe.tests.utils import FrappeTestCase
from lxml import etree

from erpnext_ec.utilities.xades_tool_v4 import sign_xml

DS = "http://www.w3.org/2000/09/xmldsig#"
NS = {"ds": DS}

SAMPLE_XML = (
	'<?xml version="1.0" ?>\n'
	'<factura id="comprobante" version="1.0.0">\n'
	"\t<infoTributaria>\n"
	"\t\t<ambiente>1</ambiente>\n"
	"\t\t<ruc>0993371265001</ruc>\n"
	"\t</infoTributaria>\n"
	"</factura>"
)


def _make_p12(password=b"test1234"):
	key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
	name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Test Signer")])
	now = datetime.datetime.now(datetime.timezone.utc)
	cert = (
		x509.CertificateBuilder()
		.subject_name(name)
		.issuer_name(name)
		.public_key(key.public_key())
		.serial_number(x509.random_serial_number())
		.not_valid_before(now - datetime.timedelta(days=1))
		.not_valid_after(now + datetime.timedelta(days=365))
		.sign(key, hashes.SHA256())
	)
	return serialization.pkcs12.serialize_key_and_certificates(
		name=b"test",
		key=key,
		cert=cert,
		cas=None,
		encryption_algorithm=serialization.BestAvailableEncryption(password),
	)


class TestSriSigning(FrappeTestCase):
	def test_signature_value_verifies(self):
		signed = sign_xml(_make_p12(), b"test1234", SAMPLE_XML)
		root = etree.fromstring(signed.encode())
		sig = root.find(".//ds:Signature", NS)
		self.assertIsNotNone(sig)

		signed_info = sig.find("ds:SignedInfo", NS)
		canon = etree.tostring(
			signed_info, method="c14n", exclusive=False, with_comments=False
		)
		sig_value = base64.b64decode(sig.find("ds:SignatureValue", NS).text)
		cert = x509.load_der_x509_certificate(
			base64.b64decode(sig.find(".//ds:X509Certificate", NS).text)
		)
		cert.public_key().verify(sig_value, canon, padding.PKCS1v15(), hashes.SHA1())

	def test_enveloped_digest_matches_original(self):
		"""Removing the Signature must yield the original document (valid digest)."""
		signed = sign_xml(_make_p12(), b"test1234", SAMPLE_XML)
		root = etree.fromstring(signed.encode())

		ref = root.find(
			'.//ds:SignedInfo/ds:Reference[@URI="#comprobante"]/ds:DigestValue', NS
		)
		self.assertIsNotNone(ref)
		expected = ref.text.strip()

		sig = root.find(".//ds:Signature", NS)
		sig.getparent().remove(sig)
		after = etree.tostring(root, method="c14n", exclusive=False, with_comments=False)
		got = base64.b64encode(hashlib.sha1(after).digest()).decode()

		self.assertEqual(got, expected)
