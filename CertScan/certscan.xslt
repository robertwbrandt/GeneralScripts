<?xml version="1.0" encoding="ascii"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:variable name="nmap_xsl_version">0.9c</xsl:variable>
<xsl:output method="text" encoding="acsii"/>

<xsl:template match="/">
	<xsl:apply-templates/>
</xsl:template>

<xsl:template match="/nmaprun/host">
	<xsl:variable name="addr" select="address/@addr" />
	<xsl:for-each select="ports/port[@protocol='tcp' and ./service/@tunnel='ssl']">
		<xsl:value-of select="$addr"/>:<xsl:value-of select="@portid"/>
	</xsl:for-each>
</xsl:template>
</xsl:stylesheet>