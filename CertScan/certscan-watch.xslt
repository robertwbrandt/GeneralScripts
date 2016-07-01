<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:output method="html" encoding="ascii"/>

<xsl:param name="lagDaily" select="24 + 4"/>
<xsl:param name="lagWeekly" select="24 * 8"/>
<xsl:param name="lagMonthly" select="24 * 32"/>

<xsl:template match="dfm-watch">
  <table border="1" align="center">
	  <caption><h2>OPW Backup Summary</h2></caption>
    <tr>
      <th align="center" height="32">Dataset Name</th>
      <th align="center">Latest Daily Backup</th>
      <th align="center">Latest Weekly Backup</th>
      <th align="center">Latest Monthly Backup</th>
      <th align="center">Latest Daily Mirror</th>
      <th align="center">Latest Weekly Mirror</th>
      <th align="center">Latest Monthly Mirror</th>
    </tr>
    <xsl:for-each select="dmz-backup">
      <xsl:sort select="translate(@name, 'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')" order="ascending" />
      <tr>
        <td><a><xsl:attribute name="href"><xsl:value-of select="@url"/></xsl:attribute><xsl:value-of select="@name"/></a></td>
        <td><xsl:if test="dailyBackup/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyBackup)">&#160;</xsl:if><xsl:value-of select="dailyBackup"/></td>
        <td><xsl:if test="weeklyBackup/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyBackup)">&#160;</xsl:if><xsl:value-of select="weeklyBackup"/></td>
        <td><xsl:if test="monthlyBackup/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyBackup)">&#160;</xsl:if><xsl:value-of select="monthlyBackup"/></td>
        <td><xsl:if test="dailyMirror/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyMirror)">&#160;</xsl:if><xsl:value-of select="dailyMirror"/></td>
        <td><xsl:if test="weeklyMirror/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyMirror)">&#160;</xsl:if><xsl:value-of select="weeklyMirror"/></td>
        <td><xsl:if test="monthlyMirror/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyMirror)">&#160;</xsl:if><xsl:value-of select="monthlyMirror"/></td>
      </tr>
    </xsl:for-each>
    <xsl:for-each select="mail-backup">
      <xsl:sort select="translate(@name, 'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')" order="ascending" />
      <tr>
        <td><a><xsl:attribute name="href"><xsl:value-of select="@url"/></xsl:attribute><xsl:value-of select="@name"/></a></td>
        <td><xsl:if test="dailyBackup/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyBackup)">&#160;</xsl:if><xsl:value-of select="dailyBackup"/></td>
        <td><xsl:if test="weeklyBackup/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyBackup)">&#160;</xsl:if><xsl:value-of select="weeklyBackup"/></td>
        <td><xsl:if test="monthlyBackup/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyBackup)">&#160;</xsl:if><xsl:value-of select="monthlyBackup"/></td>
        <td><xsl:if test="dailyMirror/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyMirror)">&#160;</xsl:if><xsl:value-of select="dailyMirror"/></td>
        <td><xsl:if test="weeklyMirror/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyMirror)">&#160;</xsl:if><xsl:value-of select="weeklyMirror"/></td>
        <td><xsl:if test="monthlyMirror/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyMirror)">&#160;</xsl:if><xsl:value-of select="monthlyMirror"/></td>
      </tr>
    </xsl:for-each>    
    <xsl:for-each select="dfm-dataset">
      <xsl:sort select="translate(@name, 'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')" order="ascending" />
      <tr>
        <td><a href="http://netapp/start.html#st=8"><xsl:value-of select="@name"/></a></td>
        <td><xsl:if test="dailyBackup/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyBackup)">&#160;</xsl:if><xsl:value-of select="dailyBackup"/></td>
        <td><xsl:if test="weeklyBackup/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyBackup)">&#160;</xsl:if><xsl:value-of select="weeklyBackup"/></td>
        <td><xsl:if test="monthlyBackup/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyBackup)">&#160;</xsl:if><xsl:value-of select="monthlyBackup"/></td>
        <td><xsl:if test="dailyMirror/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyMirror)">&#160;</xsl:if><xsl:value-of select="dailyMirror"/></td>
        <td><xsl:if test="weeklyMirror/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyMirror)">&#160;</xsl:if><xsl:value-of select="weeklyMirror"/></td>
        <td><xsl:if test="monthlyMirror/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyMirror)">&#160;</xsl:if><xsl:value-of select="monthlyMirror"/></td>
      </tr>
    </xsl:for-each>
    <xsl:for-each select="vsc-backup">
      <xsl:sort select="translate(@name, 'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')" order="ascending" />
      <tr>
        <td><a><xsl:attribute name="href"><xsl:value-of select="@url"/></xsl:attribute><xsl:value-of select="@name"/></a></td>
        <td><xsl:if test="dailyBackup/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyBackup)">&#160;</xsl:if><xsl:value-of select="dailyBackup"/></td>
        <td><xsl:if test="weeklyBackup/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyBackup)">&#160;</xsl:if><xsl:value-of select="weeklyBackup"/></td>
        <td><xsl:if test="monthlyBackup/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyBackup)">&#160;</xsl:if><xsl:value-of select="monthlyBackup"/></td>
        <td><xsl:if test="dailyMirror/@lag &gt;$lagDaily"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(dailyMirror)">&#160;</xsl:if><xsl:value-of select="dailyMirror"/></td>
        <td><xsl:if test="weeklyMirror/@lag &gt;$lagWeekly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(weeklyMirror)">&#160;</xsl:if><xsl:value-of select="weeklyMirror"/></td>
        <td><xsl:if test="monthlyMirror/@lag &gt;$lagMonthly"><xsl:attribute name="class">lag</xsl:attribute></xsl:if><xsl:if test="not(monthlyMirror)">&#160;</xsl:if><xsl:value-of select="monthlyMirror"/></td>
      </tr>
    </xsl:for-each>  
  </table>
</xsl:template>
</xsl:stylesheet>
