package com.prdct.server.api

import xml.Node

import net.liftweb.json.JsonAST.JValue
import net.liftweb.json.Xml

import java.text.SimpleDateFormat

import com.prdct.server.model.User

object RestFormatters {

  def timestamp = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'X'")

  //def restId(user: User) = {
  //"http://
  //}

  def toJSON(user: User): JValue = {
    import net.liftweb.json.JsonDSL._
    import net.liftweb.json.JsonAST._

    ("user" ->
     ("id" -> 1) ~
     ("name" -> "Matt"))
  }

  def toXml(user: User): Node = Xml.toXml(toJSON(user)).head
}
