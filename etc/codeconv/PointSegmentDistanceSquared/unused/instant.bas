Private Function PointSegmentDistanceSquared(ByVal px As Double, ByVal py As Double, ByVal p1x As Double, ByVal p1y As Double, ByVal p2x As Double, ByVal p2y As Double, ByRef t As Double, ByRef qx As Double, ByRef qy As Double) As Double
	Const kMinSegmentLenSquared As Double = 0.00000001 ' adjust to suit.  If you use float, you'll probably want something like 0.000001f
	Const kEpsilon As Double = 1.0E-14 ' adjust to suit.  If you use floats, you'll probably want something like 1E-7f
	Dim dx As Double = p2x - p1x
	Dim dy As Double = p2y - p1y
	Dim dp1x As Double = px - p1x
	Dim dp1y As Double = py - p1y
	Dim segLenSquared As Double = (dx * dx) + (dy * dy)
	If segLenSquared >= -kMinSegmentLenSquared AndAlso segLenSquared <= kMinSegmentLenSquared Then
		' segment is a point.
		qx = p1x
		qy = p1y
		t = 0.0
		Return ((dp1x * dp1x) + (dp1y * dp1y))
	Else
		' Project a line from p to the segment [p1,p2].  By considering the line
		' extending the segment, parameterized as p1 + (t * (p2 - p1)),
		' we find projection of point p onto the line. 
		' It falls where t = [(p - p1) . (p2 - p1)] / |p2 - p1|^2
		t = ((dp1x * dx) + (dp1y * dy)) / segLenSquared
		If t < kEpsilon Then
			' intersects at or to the "left" of first segment vertex (p1x, p1y).  If t is approximately 0.0, then
			' intersection is at p1.  If t is less than that, then there is no intersection (i.e. p is not within
			' the 'bounds' of the segment)
			If t > -kEpsilon Then
				' intersects at 1st segment vertex
				t = 0.0
			End If
			' set our 'intersection' point to p1.
			qx = p1x
			qy = p1y
			' Note: If you wanted the ACTUAL intersection point of where the projected lines would intersect if
			' we were doing PointLineDistanceSquared, then qx would be (p1x + (t * dx)) and qy would be (p1y + (t * dy)).
		ElseIf t > (1.0 - kEpsilon) Then
			' intersects at or to the "right" of second segment vertex (p2x, p2y).  If t is approximately 1.0, then
			' intersection is at p2.  If t is greater than that, then there is no intersection (i.e. p is not within
			' the 'bounds' of the segment)
			If t < (1.0 + kEpsilon) Then
				' intersects at 2nd segment vertex
				t = 1.0
			End If
			' set our 'intersection' point to p2.
			qx = p2x
			qy = p2y
			' Note: If you wanted the ACTUAL intersection point of where the projected lines would intersect if
			' we were doing PointLineDistanceSquared, then qx would be (p1x + (t * dx)) and qy would be (p1y + (t * dy)).
		Else
			' The projection of the point to the point on the segment that is perpendicular succeeded and the point
			' is 'within' the bounds of the segment.  Set the intersection point as that projected point.
			qx = p1x + (t * dx)
			qy = p1y + (t * dy)
		End If
		' return the squared distance from p to the intersection point.  Note that we return the squared distance
		' as an optimization because many times you just need to compare relative distances and the squared values
		' works fine for that.  If you want the ACTUAL distance, just take the square root of this value.
		Dim dpqx As Double = px - qx
		Dim dpqy As Double = py - qy
		Return ((dpqx * dpqx) + (dpqy * dpqy))
	End If
End Function
