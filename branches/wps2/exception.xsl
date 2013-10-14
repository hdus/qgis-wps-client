<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ows="http://www.opengis.net/ows/1.1" version="1.0">
<xsl:template match="ows:ExceptionReport">
<html>
  <head>
    <title>Exception Report</title>
    <style type="text/css">
      table, td, th {
        background-color:white; 
        border:1px solid green;
      }
      th {
        background-color:#83e383;
        color:white;
      }
    </style>
  </head>
  <body>
    <table>
      <tr>
        <th>Exception code</th>
        <th>Exception text</th>
      </tr>
      <xsl:for-each select="ows:Exception">
        <xsl:if test="ows:ExceptionText != ''"> 
          <tr>
            <td><xsl:value-of select="@exceptionCode"/></td> 
            <xsl:choose>
              <xsl:when test="@exceptionCode = 'JAVA_StackTrace'">
                <td><i><xsl:value-of select="ows:ExceptionText"/></i></td>
              </xsl:when>
              <xsl:otherwise>
                <td><xsl:value-of select="ows:ExceptionText"/></td>
              </xsl:otherwise>
            </xsl:choose>
          </tr>
        </xsl:if>     
      </xsl:for-each>
    </table>
  </body></html>
</xsl:template>
</xsl:stylesheet>
