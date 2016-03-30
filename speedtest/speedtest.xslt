<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" encoding="ascii"/>
	<xsl:key name="servers" match="result" use="@server"/>
	<xsl:template match="/">
	<html>
		<body>
		<style type="text/css">
				body,div,table,thead,tbody,tfoot,tr,th,td { text-align: right; color:black; font-family:\"Liberation Sans\"; font-size:x-small }
				p { text-align: center; color:black; font-family:\"Liberation Sans\"; font-size:xx-small; font-style: italic }				
				th { text-align: center; padding: 0px 10px 0px 10px; }
				td { text-align: right; padding: 0px 10px 0px 10px; white-space: nowrap; }
				tr.details:hover { background: #BBBFFF }
		</style>
		<table border="1" align="center">
		<caption>
		<h2>Line Speed Summary</h2>
		<p>Disclaimer: The values below are meant for comparisions purposes only and may not represent the actual line speed. 
		Factors such as Virtual Machines utilization, VMWare Host utilization, and access to random data may all play a role.
		How this utility works is by using a virtual server in Trim HQ to send pseudo-random data to a virtual server at a remote site.
		The data at the remote site is immediately dumped, so the figures are also not a true representations of a file transfer since we are not reading an actual file ot writing it to disk on the other side, we are only interested in the network transfer speed.
		<br/>The data shown is for the previous week.
		</p>
		</caption>
		<tr><th>Server</th><th>Overall<br/>(Mbps)</th><th>Morning<br/>(Mbps)</th><th>Lunch<br/>(Mbps)</th><th>Afternoon<br/>(Mbps)</th><th>Evening<br/>(Mbps)</th></tr>
		<xsl:for-each select="//result[generate-id(.)=generate-id(key('servers', @server)[1])]">
		<xsl:sort select="@server"/>
		<xsl:variable name="currentserver" select="@server"/>
		<xsl:variable name="hour" select="number(substring(@date,12,2))"/>

		<xsl:variable name="overalltotal" select="sum(//result[@server=$currentserver]/Mbps)"/>
		<xsl:variable name="overallcount" select="count(//result[@server=$currentserver]/Mbps)"/>
		<xsl:variable name="morningtotal" select="sum(//result[(@server=$currentserver) and (number(substring(@date,12,2)) &gt;= 8) and (number(substring(@date,12,2)) &lt; 12)]/Mbps)"/>
		<xsl:variable name="morningcount" select="count(//result[(@server=$currentserver) and (number(substring(@date,12,2)) &gt;= 8) and (number(substring(@date,12,2)) &lt; 12)]/Mbps)"/>
		<xsl:variable name="lunchtotal" select="sum(//result[(@server=$currentserver) and (number(substring(@date,12,2)) &gt;= 12) and (number(substring(@date,12,2)) &lt; 14)]/Mbps)"/>
		<xsl:variable name="lunchcount" select="count(//result[(@server=$currentserver) and (number(substring(@date,12,2)) &gt;= 12) and (number(substring(@date,12,2)) &lt; 14)]/Mbps)"/>
		<xsl:variable name="afternoontotal" select="sum(//result[(@server=$currentserver) and (number(substring(@date,12,2)) &gt;= 14) and (number(substring(@date,12,2)) &lt; 18)]/Mbps)"/>
		<xsl:variable name="afternooncount" select="count(//result[(@server=$currentserver) and (number(substring(@date,12,2)) &gt;= 14) and (number(substring(@date,12,2)) &lt; 18)]/Mbps)"/>
		<xsl:variable name="eveningtotal" select="sum(//result[(@server=$currentserver) and ((number(substring(@date,12,2)) &gt;= 18) or (number(substring(@date,12,2)) &lt; 8))]/Mbps)"/>
		<xsl:variable name="eveningcount" select="count(//result[(@server=$currentserver) and ((number(substring(@date,12,2)) &gt;= 18) or (number(substring(@date,12,2)) &lt; 8))]/Mbps)"/>

		  <tr><th><xsl:value-of select="$currentserver"/></th>
		  <td>
		  <xsl:choose>
		  <xsl:when test="$overallcount &gt; 0"><xsl:value-of select="format-number($overalltotal div $overallcount, '0.00')"/></xsl:when>
		  <xsl:otherwise>&#160;</xsl:otherwise>
		  </xsl:choose>
		  </td>
		  <td>
		  <xsl:choose>
		  <xsl:when test="$morningcount &gt; 0"><xsl:value-of select="format-number($morningtotal div $morningcount, '0.00')"/></xsl:when>
		  <xsl:otherwise>&#160;</xsl:otherwise>
		  </xsl:choose>
		  </td>
		  <td>
		  <xsl:choose>
		  <xsl:when test="$lunchcount &gt; 0"><xsl:value-of select="format-number($lunchtotal div $lunchcount, '0.00')"/></xsl:when>
		  <xsl:otherwise>&#160;</xsl:otherwise>
		  </xsl:choose>
		  </td>
		  <td>
		  <xsl:choose>
		  <xsl:when test="$afternooncount &gt; 0"><xsl:value-of select="format-number($afternoontotal div $afternooncount, '0.00')"/></xsl:when>
		  <xsl:otherwise>&#160;</xsl:otherwise>
		  </xsl:choose>
		  </td>
		  <td>
		  <xsl:choose>
		  <xsl:when test="$eveningcount &gt; 0"><xsl:value-of select="format-number($eveningtotal div $eveningcount, '0.00')"/></xsl:when>
		  <xsl:otherwise>&#160;</xsl:otherwise>
		  </xsl:choose>
		  </td>
		  </tr>
		</xsl:for-each>	
		</table>
		</body>
	</html>
	</xsl:template>

</xsl:stylesheet>



